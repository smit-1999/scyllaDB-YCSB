# list top-level just recipes
default:
    @just --list --unsorted

# list all files as a tree
tree:
    tree . -I '.git|.venv|__pycache__|debug|target|ycsb|backer.*'

# project 4 recipes
mod p4 'justmod/proj4.just'