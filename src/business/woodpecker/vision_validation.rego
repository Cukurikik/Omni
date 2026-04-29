package woodpecker.vision

default valid_vision_prompt = false

valid_vision_prompt {
    input.image_format == "JPEG"
    input.resolution >= 224
    input.text_prompt != ""
}

omni_result = {
    "value": valid_vision_prompt,
    "error": null,
    "is_ok": true
}
