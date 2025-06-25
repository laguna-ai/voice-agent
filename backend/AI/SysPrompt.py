from configuration import prompts


def build_sysPrompt(name):
    return [
        {
            "role": "system",
            "content": prompts["system_general"](name),
        }
    ]
