
# Training parameters
learning_rate = 1e-6
batch_size = 32
weight_decay = 0
momentum = 0.9
dropout = 0.5
epochs = 400
optimizer = 'sgd'


# Run configuration
resume_run = True
resume_run_id = '1xmb4jhz'
visualize_preds = False
save_model_file = 'model.pth.tar'
load_model_file = '06-04-2022_2.pth.tar'
selected_dataset = 'shape_outline_norot'
train_data_csv = 'train.csv'
test_data_csv = 'test.csv'

save_model_filepath = 'saves/' + save_model_file
# load_model_filepath = 'saves/' + selected_dataset + '/' + load_model_file
load_model_filepath = '../input/yolo-checkpoints/06-04-2022_2.pth.tar'
predictions_filepath = save_model_filepath.split('.')[0] + '_predictions.npz'


# Model and loss configuration
S = 7
B = 2
if selected_dataset == 'voc':
    C = 20
elif selected_dataset[0:5] == 'shape':
    C = 5
architecture_size = 'mini'
losses = [
    'box',
    'class',
    'obj_conf',
    'noobj_conf'
]


# Misc
num_workers = 2
pin_memory = True
device = 'cuda'
enable_wandb = True
verbose = False
