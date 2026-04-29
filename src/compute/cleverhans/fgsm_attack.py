import torch

def fgsm_attack(image, epsilon, data_grad):
    """
    CleverHans inspired Fast Gradient Sign Method (FGSM) attack.
    """
    sign_data_grad = data_grad.sign()
    perturbed_image = image + epsilon * sign_data_grad
    perturbed_image = torch.clamp(perturbed_image, 0, 1)
    return perturbed_image

def create_adversarial_example(model, image, target_label, epsilon=0.1):
    image.requires_grad = True
    output = model(image)
    loss = torch.nn.functional.nll_loss(output, target_label)
    model.zero_grad()
    loss.backward()
    data_grad = image.grad.data
    return fgsm_attack(image, epsilon, data_grad)
