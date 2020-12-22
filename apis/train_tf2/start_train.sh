out_dir=./efficientdet_d0_coco17_tpu-32/
model_dir=./efficientdet_d0_coco17_tpu-32/custom/
mkdir -p $out_dir
python model_main_tf2.py --alsologtostderr --model_dir=$model_dir --checkpoint_every_n=100  \
                         --pipeline_config_path=./ef_d0_xray.config \
                         --eval_on_train_data 2>&1 | tee $model_dir/train.log \
