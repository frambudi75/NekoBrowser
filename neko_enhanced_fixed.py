import psutil
import time
import subprocess
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
import os
import logging
from functools import lru_cache
import signal
import sys
import requests
import json
import traceback
from flask import Flask, request, jsonify
import threading

# Setup logging yang lebih efisien
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nekobrowser_enhanced.log'),
        logging.StreamHandler() if os.getenv('DEBUG') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# File untuk menyimpan URL dan pengaturan lainnya
settings_file_path = 'settings.txt'
config_file_path = 'config.json'

