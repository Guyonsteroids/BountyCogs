import discord
import os
import json
import datetime
import asyncio
import requests #Playing both sides here hehe
import aiohttp

from bs4 import BeautifulSoup
from pystreamable import StreamableApi

import moviepy.editor as mpe
from moviepy.video.io.ffmpeg_tools import *

from redbot.core import commands
from redbot.core.config import Config
