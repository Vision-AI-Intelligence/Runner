# uncomment this to run the test on CPU
export CUDA_VISIBLE_DEVICES="-1"

out_dir=./efficientdet_d0_coco17_tpu-32/custom/
mkdir -p $out_dir
python model_main_tf2.py --alsologtostderr --model_dir=$out_dir \
                         --pipeline_config_path=./ef_d0_xray.config \
                         --checkpoint_dir=$out_dir  2>&1 | tee $out_dir/eval.log
