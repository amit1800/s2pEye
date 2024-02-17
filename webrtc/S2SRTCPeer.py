import asyncio
import json
from av import VideoFrame
import logging
import time
from asgiref.sync import async_to_sync

# import cv2
import os
from django.http import HttpResponse


from django.shortcuts import render
import json
from base.views import isAuthenticated
from webrtc import customVideoTrack
from aiortc import (
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
    
)
from aiortc.contrib.media import MediaBlackhole, MediaStreamError

class S2SRTCPeer:
    def __init__(self) -> None:
        self.video = []
        self.blackhole = MediaBlackhole()

    def getS(self):
        if self.video:
            return self.video
        else:
            return None

    def object_to_string(self, obj):
        try:
            if isinstance(obj, RTCSessionDescription):
                message = {"sdp": obj.sdp, "type": obj.type}
            return json.dumps(message, sort_keys=True)
        except:
            return "error"
        
    async def handle(self, offer, nTracks, uuid, ):
        self.nTracks = nTracks
        self.uuid = uuid
        pc = RTCPeerConnection()
        serverDc = pc.createDataChannel("serverDataChannel")
        @serverDc.on("open")
        def on_open():
            print("server's data channel is open now")
        @serverDc.on("close")
        def on_close():
            print("server's data channel is closed now")
        transceiver = pc.addTransceiver(trackOrKind="video", direction="recvonly")
        transceiver.direction = "recvonly"

        # obj = self.object_from_string(request.body)
        obj = offer
        @pc.on("track")
        async def on_track(remoteSteamTrack):
            # asyncio.ensure_future(self.blackhole_consume(remoteSteamTrack))
            # self.blackhole.start()
            # self.blackhole.addTrack(remoteSteamTrack)
            # remoteSteamTrack.recv()
            # await self.blackhole.start()

            self.video.append((remoteSteamTrack))
            print("recieved video track", remoteSteamTrack.id)
        
        @pc.on("iceconnectionstatechange")
        def on_iceconnectionstatechange():
            print("ice state changed:", pc.iceConnectionState)
        
        @pc.on("datachannel")
        def on_datachannel(channel):
            print("recieved a channel")
            # channel.close()
            @channel.on("message")
            def on_message(message):
                # print("<", message)
                channel.send(message)
                pass

            @channel.on("close")
            def on_close():
                print("server data channel closed")
                pc.close()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await pc.setLocalDescription(await pc.createAnswer())
            # print("local:", pc.localDescription, "remote:", pc.remoteDescription)
            return HttpResponse(self.object_to_string(pc.localDescription))
            # return web.Response(text=object_to_string(pc.localDescription))

        else:
            print(obj)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input)
        # return web.Response(text="bad req")
        return HttpResponse(json.loads('{"msg":"helo"}'))