import argparse

from model.pretraining.data.dataloader import get_loader
from model.pretraining.data.transforms import augmentations_pretraining
from model.modeling.model import Model

from local_data.constants import *
import torch

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def process(args):
    datalaoders = get_loader(dataframes_path=args.dataframes_path, data_root_path=args.data_root_path,
                             datasets=args.datasets, balance=args.balance, batch_size=args.batch_size,
                             num_workers=args.num_workers, banned_categories=args.banned_categories,
                             caption=args.caption, augment_description=args.augment_description)

    model = Model(vision_type=args.architecture, bert_type='./Bio_ClinicalBERT', out_path=args.out_path, from_checkpoint=False, vision_pretrained=True,
                        weights_path="./local_data/results/pretraining/checkpoint.pth")

    model.fit(datalaoders, epochs=args.epochs, lr=args.lr, weight_decay=args.weight_decay, scheduler=args.scheduler,
              warmup_epoch=args.warmup_epoch, store_num=args.store_num, transforms=augmentations_pretraining)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_root_path', default=PATH_DATASETS)
    parser.add_argument('--dataframes_path', default=PATH_DATAFRAME_PRETRAIN)
    parser.add_argument('--datasets', default=["01_EYEPACS", "03_IDRID", "04_RFMid",
                                               "06_DEN", "07_LAG", "09_PAPILA", "10_PARAGUAY",
                                               "11_STARE", "14_AGAR300", "15_APTOS",
                                               "16_FUND-OCT", "17_DiaRetDB1", "19_Drishti-GS1", "20_E-ophta",
                                               "21_G1020", "23_HRF", "24_ORIGA",
                                               "26_ROC", "27_BRSET", "28_OIA-DDR", "29_AIROGS", "30_SUSTech-SYSU",
                                               "31_JICHI", "32_CHAKSU", "33_DR1-2", "34_Cataract", "35_ScarDat",
                                               "36_ACRIMA", "37_DeepDRiD"])
    parser.add_argument('--banned_categories', default=[])
    parser.add_argument('--out_path', default=PATH_RESULTS_PRETRAIN, help='output path')

    parser.add_argument('--caption', default="A fundus photograph of [CLS]")
    parser.add_argument('--augment_description', default=False, type=lambda x: (str(x).lower() == 'true'))

    parser.add_argument('--balance', default=True, type=lambda x: (str(x).lower() == 'true'))

    parser.add_argument('--epochs', default=15, type=int)
    parser.add_argument('--batch_size', default=16, type=int)
    parser.add_argument('--lr', default=1e-4, type=float, help='Learning rate')
    parser.add_argument('--weight_decay', default=1e-5, help='Weight Decay')
    parser.add_argument('--scheduler', default=False, type=lambda x: (str(x).lower() == 'true'))
    parser.add_argument('--warmup_epoch', default=0, type=int, help='number of warmup epochs')
    parser.add_argument('--store_num', default=1, type=int)

    parser.add_argument('--architecture', default='resnet_v2', help='resnet_v1 -- efficientnet')

    parser.add_argument('--num_workers', default=0, type=int, help='workers number for DataLoader')

    args, unknown = parser.parse_known_args()
    process(args=args)

if __name__ == "__main__":
    torch.cuda.set_device(1)
    main()