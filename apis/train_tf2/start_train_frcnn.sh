out_dir=../models/faster_rcnn_resnet101_v1_1024x1024_coco17_tpu-8/
model_dir=../models/xray_model_frcnn/
mkdir -p $out_dir
python model_main_tf2.py --alsologtostderr --model_dir=$model_dir --checkpoint_every_n=100  \
                         --pipeline_config_path=../models/frcnn_xray.config \
                         --eval_on_train_data 2>&1 | tee $model_dir/train.log \
