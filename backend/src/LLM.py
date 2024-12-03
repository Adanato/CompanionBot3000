from vllm import LLM, SamplingParams
import fastchat

class LLM:
    #constructor
    def __init__(self, model_name):
        self.sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_length=2048)
        self.vllm = LLM(model=model_name)
    
    def generate(self, prompt=None):
        if prompt:
            throw Error
        output = llm.generate(prompts, sampling_params)
        response = output.outputs[0].text
        return response