from builder import ShoppingAppSandboxBuilder
from creator import deploy_to_codesandbox
import asyncio
import os
builder = ShoppingAppSandboxBuilder("./yellow-template")
files = builder.build_sandbox()
result = asyncio.run(deploy_to_codesandbox(files))
        
if result.success:
    print(f"Preview: {result.preview_url}")