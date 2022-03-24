import torch
from torch import nn

from utils import intersection_over_union
from params import S, B, C

class YoloLoss(nn.Module):
    """
    YOLO loss function comparing predicted bounding boxes with actual.


    TODO: REDO CHECKING WITH GROUND TRUTH, RIGHT NOW EACH CELL ONLY HAS ONE GROUND TRUTH BOX
    """
    def __init__(self):
        super(YoloLoss, self).__init__()
        self.mse = nn.MSELoss(reduction='sum')
        self.lambda_coord = 5
        self.lambda_noobj = 0.5

    def forward(self, predictions, target):
        predictions = predictions.reshape(-1, S, S, C + B * 5)
        IOU_b1 = intersection_over_union(
            predictions[..., C+1:C+5], target[..., C+1:C+5]
        )
        IOU_b2 = intersection_over_union(
            predictions[..., C+6:C+10], target[..., C+1:C+5]
        )
        IOUs = torch.cat([IOU_b1.unsqueeze(0), IOU_b2.unsqueeze(0)], dim=0)
        _, best_box = torch.max(IOUs, dim=0)
        exists_box = target[..., C].unsqueeze(3)

        # Box loss
        box_predictions = exists_box * (
            best_box * predictions[..., C+6:C+10] +
            (1 - best_box) * predictions[..., C+1:C+5]
        )
        box_targets = exists_box * target[..., C+1:C+5]

        box_predictions[..., 2:4] = torch.sqrt(torch.abs(box_predictions[..., 2:4] + 1e-6))
        box_targets[..., 2:4] = torch.sqrt(box_targets[..., 2:4])

        box_loss = self.mse(
            torch.flatten(box_predictions, end_dim=-2),
            torch.flatten(box_targets, end_dim=-2)
        )

        # Confidence loss
        doubled_exists_box = torch.cat([exists_box.unsqueeze(0), exists_box.unsqueeze(0)], dim=0)
        pred_conf = torch.cat([predictions[..., C:C+1].unsqueeze(0), predictions[..., C+5:C+6].unsqueeze(0)], dim=0)
        obj_conf_loss = self.mse(
            torch.flatten(doubled_exists_box * pred_conf),
            torch.flatten(doubled_exists_box * IOUs)
        )
        noobj_conf_loss = self.mse(
            torch.flatten((1 - doubled_exists_box) * pred_conf),
            torch.flatten((1 - doubled_exists_box) * IOUs)
        )

        # Class loss
        class_loss = self.mse(
            torch.flatten(exists_box * predictions[..., :C], end_dim=-2),
            torch.flatten(exists_box * target[..., :C], end_dim=-2)
        )

        # Total loss
        loss = (
            self.lambda_coord * box_loss +
            obj_conf_loss +
            self.lambda_noobj * noobj_conf_loss +
            class_loss
        )
        return loss