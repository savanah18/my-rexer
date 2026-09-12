"""
MCP HTTP server for LLM client integration.

Serves as the entry point for HTTP-based MCP protocols.
"""

from flask import Flask, request, jsonify
import logging


logger = logging.getLogger(__name__)


app = Flask(__name__)