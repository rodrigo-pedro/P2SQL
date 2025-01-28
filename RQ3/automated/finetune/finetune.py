import torch
import torch.nn as nn
import transformers
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    TrainingArguments,
)

from trl import SFTTrainer
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from datasets import load_dataset
import os


model_name = "mistralai/Mistral-7B-Instruct-v0.2"
file_name = "all_attacks_dataset_LANGCHAIN.json"

tokenizer = AutoTokenizer.from_pretrained(model_name, add_eos_token=True)


dataset_train = load_dataset("json", data_files=file_name, split="train")

dataset_train = dataset_train.map(
    lambda x: {
        "formatted_data": tokenizer.apply_chat_template(
            x["data"],
            tokenize=False,
        )
    }
)


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    quantization_config=bnb_config,
    attn_implementation="flash_attention_2",
)

model.config.use_cache = False  # Disable cache for fine-tuning. We always want to use the most recent values.
model.gradient_checkpointing_enable()

peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=32,  # 8
    bias="none",
    task_type="CAUSAL_LM",
)
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, peft_config)

tokenizer.padding_side = "right"
tokenizer.pad_token = tokenizer.eos_token
tokenizer.pad_token_id = tokenizer.eos_token_id

os.environ["WANDB_PROJECT"] = "p2sql"

training_args = TrainingArguments(
    output_dir="output",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    num_train_epochs=8,
    warmup_ratio=0.03,
    max_grad_norm=0.3,
    fp16=False,
    bf16=False,
    save_strategy="epoch",  # save at end of epoch. Alternative is "steps", which saves at every "save_steps"
    logging_steps=1,
    learning_rate=2e-4,
    group_by_length=True,
    lr_scheduler_type="constant",
    optim="paged_adamw_8bit",
    gradient_checkpointing=True,
    report_to="wandb",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset_train,
    peft_config=peft_config,
    max_seq_length=2048,
    dataset_text_field="formatted_data",
    args=training_args,
    packing=True,
)

trainer.train()
trainer.save_model("p2sql-model-mistral-7b-all-attacks-LANGCHAIN-8")
