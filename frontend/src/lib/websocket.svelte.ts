import { authStore } from './stores/auth.svelte';
import { PUBLIC_WS_BASE } from '$env/static/public';

type WSMessage = {
	type: string;
	issue_id?: string;
};

type MessageHandler = (msg: WSMessage) => void;

class WebSocketClient {
	private socket: WebSocket | null = null;
	private handlers: Set<MessageHandler> = new Set();
	private pingTimer: ReturnType<typeof setInterval> | null = null;
	private room: string = '';
	private reconnectDelay = 1000;

	connect(room: string) {
		this.room = room;
		const token = authStore.accessToken;
		if (!token) return;

		this.socket = new WebSocket(`${PUBLIC_WS_BASE}/ws/${room}?token=${token}`);

		this.socket.onopen = () => {
			this.reconnectDelay = 1000;
			this.startPing();
		};

		this.socket.onmessage = (event) => {
			try {
				const msg = JSON.parse(event.data) as WSMessage;
				this.handlers.forEach((h) => h(msg));
			} catch {
				// oops, ignore la
			}
		};
		this.socket.onclose = () => {
			this.stopPing();
			setTimeout(() => {
				if (this.room) this.connect(this.room);
			}, this.reconnectDelay);
			this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
		};
		this.socket.onerror = () => {
			this.socket?.close();
		};
	}

	disconnect() {
		this.room = '';
		this.stopPing();
		this.socket?.close();
		this.socket = null;
	}

	onMessage(handler: MessageHandler) {
		this.handlers.add(handler);
		return () => this.handlers.delete(handler);
	}

	private startPing() {
		this.pingTimer = setInterval(() => {
			if (this.socket?.readyState === WebSocket.OPEN) {
				this.socket.send('ping');
			}
		}, 25000);
	}

	private stopPing() {
		if (this.pingTimer) clearInterval(this.pingTimer);
	}
}

export const wsClient = new WebSocketClient();
