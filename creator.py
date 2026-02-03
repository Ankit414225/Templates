"""
CodeSandbox Integration Module
==============================
Creates CodeSandbox previews from sandbox_builder files
Uses existing project files without generating extras
"""

import os
import httpx
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SandboxResult:
    """Result from CodeSandbox creation."""
    success: bool
    sandbox_id: Optional[str] = None
    embed_url: Optional[str] = None
    preview_url: Optional[str] = None
    error: Optional[str] = None


class CodeSandboxClient:
    """
    Client for creating CodeSandbox previews from existing project files.
    Integrates with SandboxBuilder to use real project structure.
    """

    API_URL = "https://codesandbox.io/api/v1/sandboxes/define?json=1"

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = 'csb_v1_k3HPs8nUQCNjE5RsFQxw6JHiiCA9xxQ1YWqkr5IzDGs'

    async def create_sandbox_from_builder(
        self,
        sandbox_files: Dict[str, Dict[str, str]],
        title: Optional[str] = None
    ) -> SandboxResult:
        """
        Create a CodeSandbox preview from SandboxBuilder files.
        
        Args:
            sandbox_files: Files dict from SandboxBuilder.build_sandbox()
            title: Optional custom title
        """
        
        title = title or f"Shopping App – {datetime.now():%Y%m%d_%H%M%S}"

        payload = {"files": sandbox_files}

        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                # Raise for non-2xx responses
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError:
                    return SandboxResult(
                        success=False,
                        error=f"API Error {resp.status_code}: {resp.text[:200]}",
                    )

                # Ensure response is valid JSON
                try:
                    data = resp.json()
                except ValueError:
                    return SandboxResult(success=False, error="Invalid JSON response from API")

                sandbox_id = data.get("sandbox_id")
                if not sandbox_id:
                    return SandboxResult(success=False, error="No sandbox_id in response")

                embed_url = f"https://codesandbox.io/embed/{sandbox_id}?fontsize=14&hidenavigation=1&theme=dark&view=preview"
                preview_url = f"https://codesandbox.io/s/{sandbox_id}"

                return SandboxResult(
                    success=True,
                    sandbox_id=sandbox_id,
                    embed_url=embed_url,
                    preview_url=preview_url,
                )

            except httpx.RequestError as e:
                return SandboxResult(success=False, error=f"Request error: {e}")
            except Exception as e:
                return SandboxResult(success=False, error=str(e))

    async def create_sandbox(
        self,
        files: Dict[str, Dict[str, str]],
        title: Optional[str] = None
    ) -> SandboxResult:
        """Alias for create_sandbox_from_builder"""
        return await self.create_sandbox_from_builder(files, title)


# ============================================================================
# CONVENIENCE WRAPPER
# ============================================================================

async def deploy_to_codesandbox(
    sandbox_files: Dict[str, Dict[str, str]],
    title: Optional[str] = None
) -> SandboxResult:
    """
    Deploy sandbox files to CodeSandbox.
    
    Example:
        from sandbox_builder import ShoppingAppSandboxBuilder
        from codesandbox_client import deploy_to_codesandbox
        import asyncio
        
        builder = ShoppingAppSandboxBuilder(Path("e:/shopping"))
        files = builder.build_sandbox()
        result = asyncio.run(deploy_to_codesandbox(files))
        
        if result.success:
            print(f"Preview: {result.preview_url}")
    """
    client = CodeSandboxClient()
    return await client.create_sandbox(sandbox_files, title)