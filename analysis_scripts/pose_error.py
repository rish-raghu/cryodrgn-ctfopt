# Adapted courtesy of Axel Levy

import numpy as np
import torch
import argparse
import pickle

def get_ref_matrix(r1, r2, i, flip=False):
    if flip:
        return np.matmul(r2[i].T, _flip(r1[i]))
    else:
        return np.matmul(r2[i].T, r1[i])


def _flip(rot):
    x = np.diag([1, 1, -1]).astype(rot.dtype)
    return np.matmul(x, rot)


def align_rot(r1, r2, i, flip=False):
    if flip:
        return np.matmul(_flip(r2), get_ref_matrix(r1, r2, i, flip=True))
    else:
        return np.matmul(r2, get_ref_matrix(r1, r2, i, flip=False))


def frob_norm(A, B):
    return np.linalg.norm(A - B, axis=(1,2))


def align_rot_best(rot_gt_tensor, rot_pred_tensor, n_tries=100):
    """
    rot_gt_tensor: [n_rots, 3, 3]
    rot_pred_tensor: [n_rots, 3, 3]
    n_tries: int

    output: [n_rots, 3, 3] (numpy), float
    """
    # rot_gt = rot_gt_tensor.clone().numpy()
    # rot_pred = rot_pred_tensor.clone().numpy()
    rot_gt = rot_gt_tensor.copy()
    rot_pred = rot_pred_tensor.copy()

    median = []
    for i in range(n_tries):
        rot_pred_aligned = align_rot(rot_gt, rot_pred, i, flip=False)
        dists = frob_norm(rot_gt, rot_pred_aligned)
        median.append(np.median(dists))

    median_flip = []
    for i in range(n_tries):
        rot_pred_aligned = align_rot(rot_gt, rot_pred, i, flip=True)
        dists = frob_norm(rot_gt, rot_pred_aligned)
        median_flip.append(np.median(dists))

    if np.min(median) < np.min(median_flip):
        #utils.log("Correct Handedness")
        i_best = np.argmin(median)
        alignment_matrix = get_ref_matrix(rot_gt, rot_pred, i_best, flip=False)
        rot_pred_aligned = np.matmul(rot_pred, alignment_matrix)
        rot_gt_aligned = np.matmul(rot_gt, alignment_matrix.T)
        median_frob = np.min(median)
    else:
        #utils.log("Flipped Handedness")
        i_best = np.argmin(median_flip)
        alignment_matrix = get_ref_matrix(rot_gt, rot_pred, i_best, flip=True)
        rot_pred_aligned = np.matmul(_flip(rot_pred), alignment_matrix)
        rot_gt_aligned = _flip(np.matmul(rot_gt, alignment_matrix.T))
        median_frob = np.min(median_flip)

    return rot_pred_aligned, rot_gt_aligned, median_frob

def get_trans_metrics(trans_gt, trans_pred, rotmat, correct_global_trans=False):
    trans_gt_corr = trans_gt

    if correct_global_trans:
        b = torch.cat([(trans_pred - trans_gt_corr)[:, 0], (trans_pred - trans_gt_corr)[:, 1]], 0)
        matrix_a = torch.cat([rotmat[:, 0, :], rotmat[:, 1, :]], 0)
        u = torch.tensor(np.linalg.lstsq(matrix_a, b)[0])
        matrix_n = torch.tensor([[1, 0, 0], [0, 1, 0]]).reshape(1, 2, 3).float()
        batch_size = rotmat.shape[0]
        trans_pred_corr = trans_pred - torch.bmm(matrix_n.repeat(batch_size, 1, 1),
                                                 (u @ rotmat.permute(0, 2, 1)).reshape(-1, 3, 1)).reshape(-1, 2)
    else:
        trans_pred_corr = trans_pred

    #dist = np.sum((trans_gt_corr.numpy() - trans_pred_corr.numpy()) ** 2, axis=1)
    dist = np.sum((trans_gt_corr - trans_pred_corr) ** 2, axis=1)

    mse = np.mean(dist)
    medse = np.median(dist)

    return trans_pred_corr, trans_gt_corr, mse, medse

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Compute rotational and translational error between sets of poses")
    parser.add_argument('refPose', help='Ground trouth pose pkl file')
    parser.add_argument('inPoses', nargs='*', help='List of input pose pkl files')
    #parser.add_argument('-o', required=True, help='Output txt file')
    parser.add_argument('--ind', help="Pkl file of indices from refPose to use")
    args = parser.parse_args()

    f = open(args.refPose, "rb")
    refPose = pickle.load(f)
    if args.ind:
        f = open(args.ind, "rb")
        ind = pickle.load(f)
        refRot = refPose[0][ind]
        refTrans = refPose[1][ind]
    else:
        refRot = refPose[0]
        refTrans = refPose[1]

    rotErrs, transErrs, epochs = [], [], []
    for file in args.inPoses:
        epochs.append(int(file.split(".")[-2]))
        f = open(file, "rb")
        predPose = pickle.load(f)
        rot_pred_aligned, rot_gt_aligned, median_frob = align_rot_best(refRot, predPose[0])
        trans_pred_corr, trans_gt_corr, mse, medse = get_trans_metrics(refTrans, predPose[1], predPose[0])
        rotErrs.append(median_frob)
        transErrs.append(medse)

    rotErrs = np.array(rotErrs)[np.argsort(epochs)]
    transErrs = np.array(transErrs)[np.argsort(epochs)]

    print("Rotation median errors: ", rotErrs)
    print("Translation median errors: ", transErrs)
    print("Lowest rotation error: ", np.min(rotErrs))
    print("Lowest translation error: ", np.min(transErrs))
    print("Lowest rotation error epoch: ", epochs[np.argmin(rotErrs)])
    print("Lowest translation error epoch: ", epochs[np.argmin(transErrs)])
