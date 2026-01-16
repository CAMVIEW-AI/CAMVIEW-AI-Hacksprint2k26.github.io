import numpy as np
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment


# -----------------------------
# IOU FUNCTION
# -----------------------------
def iou(bb_test, bb_gt):
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])

    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)

    inter = w * h
    area1 = (bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
    area2 = (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1])

    return inter / (area1 + area2 - inter + 1e-6)


# -----------------------------
# KALMAN TRACKER
# -----------------------------
class KalmanBoxTracker:
    count = 0

    def __init__(self, bbox):
        self.kf = KalmanFilter(dim_x=7, dim_z=4)

        self.kf.F = np.array([
            [1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0],
            [0,0,1,0,0,0,1],
            [0,0,0,1,0,0,0],
            [0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0],
            [0,0,0,0,0,0,1]
        ])

        self.kf.H = np.array([
            [1,0,0,0,0,0,0],
            [0,1,0,0,0,0,0],
            [0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0]
        ])

        self.kf.R *= 10
        self.kf.P *= 10
        self.kf.Q *= 0.01

        self.kf.x[:4] = bbox.reshape((4,1))

        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def update(self, bbox):
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(bbox.reshape((4,1)))

    def predict(self):
        self.kf.predict()
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        return self.kf.x[:4].reshape((4,))

    def get_state(self):
        return self.kf.x[:4].reshape((4,))


# -----------------------------
# SORT TRACKER
# -----------------------------
class Sort:
    def __init__(self, max_age=15, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0

    def update(self, dets=np.empty((0, 5))):
        self.frame_count += 1

        trks = np.zeros((len(self.trackers), 4))
        to_del = []

        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            trks[t] = pos
            if np.any(np.isnan(pos)):
                to_del.append(t)

        for t in reversed(to_del):
            self.trackers.pop(t)

        matched, unmatched_dets, unmatched_trks = self.associate(dets, trks)

        for m in matched:
            self.trackers[m[1]].update(dets[m[0], :4])

        for i in unmatched_dets:
            self.trackers.append(KalmanBoxTracker(dets[i, :4]))

        ret = []
        for trk in self.trackers:
            if trk.time_since_update < 1 and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                bbox = trk.get_state()
                ret.append(np.concatenate((bbox, [trk.id])))

        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        return np.array(ret)

    def associate(self, dets, trks):
        if len(trks) == 0:
            return np.empty((0,2), dtype=int), np.arange(len(dets)), np.empty((0), dtype=int)

        iou_matrix = np.zeros((len(dets), len(trks)), dtype=np.float32)

        for d, det in enumerate(dets):
            for t, trk in enumerate(trks):
                iou_matrix[d, t] = iou(det[:4], trk)

        row_ind, col_ind = linear_sum_assignment(-iou_matrix)

        matched = []
        unmatched_dets = []
        unmatched_trks = []

        for d in range(len(dets)):
            if d not in row_ind:
                unmatched_dets.append(d)

        for t in range(len(trks)):
            if t not in col_ind:
                unmatched_trks.append(t)

        for r, c in zip(row_ind, col_ind):
            if iou_matrix[r, c] < self.iou_threshold:
                unmatched_dets.append(r)
                unmatched_trks.append(c)
            else:
                matched.append((r, c))

        return np.array(matched), np.array(unmatched_dets), np.array(unmatched_trks)
