#!/usr/bin/env bash

# =============================================================================
# Multi-GPU Training Script for InternImage Detection
# =============================================================================
# 
# This script runs distributed training on multiple GPUs on a single machine.
# Supports all train.py parameters with comprehensive argument parsing.
#
# Usage: ./train_multi_gpu.sh <config_file> <num_gpus> [train_options]
# 
# Train Options:
#   --work-dir DIR              : Directory to save logs and models
#   --resume-from PATH          : Checkpoint file to resume from
#   --auto-resume               : Resume from latest checkpoint automatically
#   --no-validate               : Skip validation during training
#   --seed INT                  : Random seed
#   --diff-seed                 : Use different seeds for different ranks
#   --deterministic             : Set deterministic options for CUDNN
#   --cfg-options KEY=VALUE     : Override config settings
#   --auto-scale-lr             : Enable automatic learning rate s caling
#
# Examples:
#   ./train_multi_gpu.sh configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4
#   ./train_multi_gpu.sh configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4 --work-dir ./my_experiment --seed 42
#   ./train_multi_gpu.sh configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4 --auto-resume --cfg-options optimizer.lr=0.001
# =============================================================================

set -e  # Exit on any error

# Function to show usage
show_usage() {
    echo "Usage: $0 <config_file> <num_gpus> [train_options]"
    echo ""
    echo "Required Arguments:"
    echo "  config_file          : Path to the configuration file"
    echo "  num_gpus             : Number of GPUs to use"
    echo ""
    echo "Optional Train Options:"
    echo "  --work-dir DIR       : Directory to save logs and models"
    echo "  --resume-from PATH   : Checkpoint file to resume from"
    echo "  --auto-resume        : Resume from latest checkpoint automatically"
    echo "  --no-validate        : Skip validation during training"
    echo "  --seed INT           : Random seed"
    echo "  --diff-seed          : Use different seeds for different ranks"
    echo "  --deterministic      : Set deterministic options for CUDNN"
    echo "  --cfg-options KEY=VALUE : Override config settings"
    echo "  --auto-scale-lr      : Enable automatic learning rate scaling"
    echo ""
    echo "Examples:"
    echo "  $0 configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4"
    echo "  $0 configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4 --work-dir ./my_experiment --seed 42"
    echo "  $0 configs/coco/dino_4scale_cbinternimage_h_objects365_coco_ss.py 4 --auto-resume"
}

# Check if required arguments are provided
if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments!"
    echo ""
    show_usage
    exit 1
fi

# Parse required arguments
CONFIG=$1
GPUS=$2
shift 2  # Remove first two arguments, keep the rest for train options

# Validate required inputs
if [ ! -f "$CONFIG" ]; then
    echo "Error: Config file '$CONFIG' not found!"
    exit 1
fi

if ! [[ "$GPUS" =~ ^[0-9]+$ ]] || [ "$GPUS" -lt 1 ]; then
    echo "Error: Number of GPUs must be a positive integer!"
    exit 1
fi

# Check if GPUs are available
if ! command -v nvidia-smi &> /dev/null; then
    echo "Error: nvidia-smi not found. Are you on a machine with NVIDIA GPUs?"
    exit 1
fi

AVAILABLE_GPUS=$(nvidia-smi --list-gpus | wc -l)
if [ "$GPUS" -gt "$AVAILABLE_GPUS" ]; then
    echo "Error: Requested $GPUS GPUs, but only $AVAILABLE_GPUS are available!"
    exit 1
fi

# Set communication port (for inter-GPU communication)
# You can override this by setting PORT environment variable
COMMUNICATION_PORT=${PORT:-18689}

# Parse train options and build command
TRAIN_ARGS=""
# 这些参数本来就是加在python那行的（见下方 $TRAIN_ARGS 的用法），
# 这里只是把所有传入的参数解析出来，拼接到 TRAIN_ARGS 变量里，
# 最后一并加到 python 命令行后面。
# 你也可以不做参数解析，直接把 "$@" 加到 python 那行后面，
# 但这样就无法做参数校验、帮助信息、错误提示等自定义处理了。
while [[ $# -gt 0 ]]; do
    case $1 in
        --work-dir)
            TRAIN_ARGS="$TRAIN_ARGS --work-dir $2"
            shift 2
            ;;
        --resume-from)
            TRAIN_ARGS="$TRAIN_ARGS --resume-from $2"
            shift 2
            ;;
        --auto-resume)
            TRAIN_ARGS="$TRAIN_ARGS --auto-resume"
            shift
            ;;
        --no-validate)
            TRAIN_ARGS="$TRAIN_ARGS --no-validate"
            shift
            ;;
        --seed)
            TRAIN_ARGS="$TRAIN_ARGS --seed $2"
            shift 2
            ;;
        --diff-seed)
            TRAIN_ARGS="$TRAIN_ARGS --diff-seed"
            shift
            ;;
        --deterministic)
            TRAIN_ARGS="$TRAIN_ARGS --deterministic"
            shift
            ;;
        --cfg-options)
            TRAIN_ARGS="$TRAIN_ARGS --cfg-options $2"
            shift 2
            ;;
        --auto-scale-lr)
            TRAIN_ARGS="$TRAIN_ARGS --auto-scale-lr"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Starting Multi-GPU Training"
echo "=========================================="
echo "Config file: $CONFIG"
echo "Number of GPUs: $GPUS"
echo "Communication port: $COMMUNICATION_PORT"
echo "Train arguments: $TRAIN_ARGS"
echo "=========================================="

# Set Python path to include the project root
export PYTHONPATH="$(dirname $0)/..:$PYTHONPATH"

# Run distributed training
# Use torchrun instead of torch.distributed.launch (newer PyTorch versions)
torchrun \
    --nproc_per_node=$GPUS \
    --master_port=$COMMUNICATION_PORT \
    "$(dirname "$0")/train.py" \
    "$CONFIG" \
    --launcher pytorch \
    $TRAIN_ARGS

echo "=========================================="
echo "Training completed!"
echo "==========================================" 