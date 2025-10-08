# Backup of current simple version
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import requests
import time

# This is the backup of the simple version