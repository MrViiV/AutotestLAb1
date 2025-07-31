terraform {
  required_providers {
    random = {
      source = "hashicorp/random"
    }
  }
}

provider "random" {}

resource "random_pet" "example" {
  length    = 2
  separator = "-"
}

output "pet_name" {
  value = random_pet.example.id
}
