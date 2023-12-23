import sys, json, os, re
import requests
import random
import numpy as np
import os
import openai
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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"
)

def llm4(msgs) -> str:
    return client.chat.completions.create(
        model='openai/gpt-4',
        messages=msgs,
        temperature=0.0001).choices[0].message.content
