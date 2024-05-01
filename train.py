import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers import AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
import math


model_path = "deepseek-ai/deepseek-coder-6.7b-base"
#model_path = "bigcode/starcoder2-3b"

tokenizer = AutoTokenizer.from_pretrained(model_path, token=access_token)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    ),
    device_map="auto"
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    set_peft_model_state_dict
)

import torch

lora_rank = 32
lora_alpha = 64
lora_dropout = 0.06

config = LoraConfig(
    r=lora_rank,
    lora_alpha=lora_alpha,
    lora_dropout=lora_dropout,
    bias="none",
    task_type="CAUSAL_LM"
)

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)
lora_model = get_peft_model(model, config)

from datasets import load_dataset

dataset = load_dataset('json', data_files='vala_dataset_0.5.json')

td = dataset
data = td.map(lambda samples: tokenizer(samples["text"]), batched=True)


from transformers import IntervalStrategy
import os

os.makedirs("out", exist_ok=True)
micro_batch_size = 1
batch_size = 256
gradient_accumulation_steps = batch_size // micro_batch_size
warmup_steps = 7
eval_steps = 100
epochs = 3
actual_lr = 2e-4
lr_scheduler_type = 'cosine_with_restarts'
trainer = Trainer(
    model=lora_model,
    train_dataset=data["train"],
    #eval_dataset=tokenized_datasets,
    args=TrainingArguments(
        save_strategy=IntervalStrategy.STEPS,
        save_steps=30,
        save_total_limit=5,
        per_device_train_batch_size=micro_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_steps=warmup_steps,
        num_train_epochs=epochs,
        learning_rate=actual_lr,
        fp16=True,
        optim='adamw_bnb_8bit',
        logging_steps=2,
        evaluation_strategy="no",
        #eval_steps=math.ceil(eval_steps / gradient_accumulation_steps),
        lr_scheduler_type=lr_scheduler_type,
        ddp_find_unused_parameters=None,
        output_dir="out",
    ),
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)
tokenizer.pad_token = tokenizer.eos_token

trainer.train()

from peft import PeftModel
trainer.model.save_pretrained("./lora_out")


