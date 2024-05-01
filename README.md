# ValaBot

*A better bot for coding in Vala*

I fine tuned the Deepseek-Coder-6.7B model on the Vala programming language. It is significantly better at helping to write Vala/Gtk+ applications than other coding assistants such as Copilot. 

![deepseek-vala](https://github.com/supercamel/ValaBot/assets/7779685/cbd00f3f-1268-4773-b90e-fcd20c591114)


Here is Github Copilot for comparison

![copilot_is_clueless](https://github.com/supercamel/ValaBot/assets/7779685/9f0675ef-5332-4a5a-8ce8-b6491aad299c)

Deepseek-Coder-6.7B-Vala produces more accurate snippets which makes it much quicker and easier to write code in Vala. 

The model is freely available on Huggingface: https://huggingface.co/scowen/deepseek-coder-6.7b-vala/tree/main

It can be used with TabbyML: https://github.com/TabbyML/tabby

## Server Setup 

You will require a half decent GPU to run this bot well. You'll need probably 12GB of VRAM. Something like an RTX 3060 or RX 6800 is fine. 

for nvidia





```
docker run -it   --gpus all -p 8080:8080 -v $HOME/.tabby:/data   tabbyml/tabby   serve --model supercamel/DeepseekCoder-6.7B-Vala --device cuda
```


for amd
```
sudo docker run -it   --device /dev/dri --device /dev/kfd   -p 8080:8080 -v $HOME/.tabby:/data   tabbyml/tabby-rocm   serve --model supercamel/DeepseekCoder-6.7B-Vala --device rocm
```


### RAG

Adding some Git repositories for RAG is helpful. RAG (retrieval augmented generation) is a feature of TabbyML that can improve code generation by searching for similar snippets of code to provide to the AI model. 
The model can then refer to those snippets as it generates new code.

In your tabby config 
~/.tabby/config.toml

```
[[repositories]]
name = "ValaGtkExamples"
git_url = "https://github.com/gerito1/vala-gtk-examples"

[[repositories]]
name = "ValaExamples"
git_url = "https://github.com/supercamel/ValaExamples"
```

add/remove repos as required. run this command to force tabby to index the repos right away. 

nvidia
```
sudo docker run -t --gpus=all -v $HOME/.tabby:/data tabbyml/tabby scheduler --now
```

amd
```
sudo docker run -it   --device /dev/dri --device /dev/kfd -v $HOME/.tabby:/data   tabbyml/tabby-rocm  scheduler --now
```

## Client Setup

### VSCode

In VSCode, simply install the TabbyML plugin. 

### VIM (Ubuntu 22.04)

Install NVM (if you don't already have it)
```
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.bashrc
```

Use NVM to install Node 20.12.2
```
nvm install 20.12.2
nvm alias default 20.12.2
```

Install VIM version 9.0 from this PPA

```
sudo add-apt-repository ppa:jonathonf/vim
sudo apt update
sudo apt install vim
```

Now follow the instructions on the tabby-vim repo: https://github.com/TabbyML/vim-tabby

Alternatively, you may setup vim using this configuration script which will also install plugins for Vala syntax highlighting. 

```
git clone https://github.com/supercamel/vim
cd vim
chmod 755 setup_vim.sh
./setup_vim.sh
```
