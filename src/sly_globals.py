
import os, sys
from pathlib import Path
import supervisely as sly


my_app = sly.AppService()
api: sly.Api = my_app.public_api

root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

logger = sly.logger

train_ds = os.environ["modal.state.train"]
val_ds = os.environ["modal.state.val"]
test_ds = os.environ["modal.state.test"]

datasets = []

for ds in [train_ds, val_ds, test_ds]:
    if len(ds) != 2:
        datasets.append(ds[1:-1].replace('\'', ''))

# datasets = ['Val'] # TODO debug

if len(datasets) == 0:
    logger.warn('You have not selected a dataset to import')
    my_app.stop()

train_percent = int(os.environ["modal.state.samplePercentTrain"])
val_percent = int(os.environ["modal.state.samplePercentVal"])
test_percent = int(os.environ["modal.state.samplePercentTest"])

# train_percent = 20 # TODO debug
# val_percent = 20 # TODO debug
# test_percent = 20 # TODO debug

sample_img_count = {'Train': 4 * train_percent, 'Val': int(0.5 * val_percent), 'Test': int(0.5 * test_percent)}

project_name = 'coffee'
work_dir = 'coffee_data'
coffee_url = 'https://docs.google.com/uc?id=15YHebAGrx1Vhv8-naave-R5o3Uo70jsm'

arch_name = 'coffee-datasets.zip'
images_folder = 'segmentation/images'
anns_folder = 'segmentation/annotations'
symptom_tag_file = 'leaf/dataset.csv'
ann_ext = '_mask.png'

batch_size = 30

obj_classes_names = ['symptom', 'leaf']
symptom_idx = 0
leaf_idx = 1
obj_class_color_idxs = [255, 176]
symptom_color = [255, 0, 0]
leaf_color = [0, 176, 0]

obj_class_leaf = sly.ObjClass(obj_classes_names[1], sly.Bitmap, color=leaf_color)
obj_class_symptom = sly.ObjClass(obj_classes_names[0], sly.Bitmap, color=symptom_color)

obj_classes = [obj_class_symptom, obj_class_leaf]
obj_class_collection = sly.ObjClassCollection(obj_classes)

tags_data = {}
tag_names = ['predominant_stress', 'miner', 'rust', 'phoma', 'cercospora', 'severity']
tag_metas = []
for tag_name in tag_names:
    tag_meta = sly.TagMeta(tag_name, sly.TagValueType.ANY_NUMBER)
    tag_metas.append(tag_meta)

tag_meta_collection = sly.TagMetaCollection(tag_metas)

meta = sly.ProjectMeta(obj_classes=obj_class_collection, tag_metas=tag_meta_collection)

storage_dir = my_app.data_dir
work_dir_path = os.path.join(storage_dir, work_dir)
sly.io.fs.mkdir(work_dir_path)
archive_path = os.path.join(work_dir_path, arch_name)
