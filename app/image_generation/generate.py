import torch
from diffusers import AutoPipelineForImage2Image
from diffusers.utils import make_image_grid, load_image
from app.utils import utils

pipeline = AutoPipelineForImage2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
)


pipeline.enable_model_cpu_offload()
# remove following line if xFormers is not installed or you have PyTorch 2.0 or higher installed
pipeline.enable_xformers_memory_efficient_attention()


def run(image_url, prompt):
    
    init_image = load_image(image_url)

    negative_prompt = "ugly, deformed, disfigured, poor details, bad anatomy"

    # pass prompt and image to pipeline
    image = pipeline(prompt, negative_prompt=negative_prompt, image=init_image).images[0]
    image_name = utils.generate_secure_random_image_name('.png') 
    output_path = "app/static/results/" + image_name  # Define the output path
    image.save(output_path)  # Save the image to the specified path
    # make_image_grid([init_image, image], rows=1, cols=2)
    
    return output_path
    