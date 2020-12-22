out_dir=../models/centernet_hg104_512x512_coco17_tpu-8/
model_dir=../models/xray_model_centernet/
mkdir -p $out_dir
python model_main_tf2.py --alsologtostderr --model_dir=$model_dir --checkpoint_every_n=100  \
                         --pipeline_config_path=../models/center_net_xray.config \
                         --eval_on_train_data 2>&1 | tee $model_dir/train.log \
