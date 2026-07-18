from typing import Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from backend.services.playground.playground_service import PlaygroundService
from backend.domain.session import AISession
from backend.domain.events import (
    StreamEvent, GenerationStarted, TokenReceived, GenerationCompleted, 
    GenerationFailed, GenerationCancelled
)

class PlaygroundWidget(QFrame):
    """
    Decoupled, reusable component for AI interactions.
    Manages its own AISession and communicates with PlaygroundService.
    """
    
    def __init__(self, ctx, provider_id: str = ""):
        super().__init__()
        self.ctx = ctx
        self.provider_id = provider_id
        self.service = PlaygroundService()
        self.session = AISession(provider_id=self.provider_id)
        
        self.current_task_id = None
        self._build_ui()
        
    def set_provider(self, provider_id: str):
        self.provider_id = provider_id
        self.session.provider_id = provider_id

    def _build_ui(self):
        self.setObjectName("PlaygroundCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame#PlaygroundCard {
                background-color: transparent;
                border: none;
            }
            QLabel[class="HeaderLabel"] {
                font-size: 16px;
                font-weight: 700;
                color: #E2E8F0;
                padding-bottom: 4px;
            }
            QLabel[class="SubHeader"] {
                color: #94A3B8; 
                font-size: 11px; 
                font-weight: 600; 
                text-transform: uppercase; 
                letter-spacing: 1px;
            }
            QTextEdit {
                background-color: #13161C;
                border: 1px solid #1E2530;
                border-radius: 6px;
                color: #E2E8F0;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton[class="PrimaryBtn"] {
                background-color: #E2E8F0;
                color: #0F172A;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton[class="PrimaryBtn"]:hover {
                background-color: #F8FAFC;
            }
            QPushButton[class="DangerBtn"] {
                background-color: #EF4444;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton[class="GhostBtn"] {
                background: transparent; 
                color: #64748B; 
                border: none; 
                border-radius: 8px;
                font-size: 13px; 
                font-weight: 600; 
                padding: 6px 12px;
            }
            QPushButton[class="GhostBtn"]:hover {
                background: #1E2530;
                color: #E2E8F0;
            }
        """)
        
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # ── HEADER ──
        header_row = QHBoxLayout()
        header = QLabel("⚡ Interactive Playground")
        header.setProperty("class", "HeaderLabel")
        header_row.addWidget(header)
        
        self.footer_label = QLabel("Ready")
        self.footer_label.setStyleSheet("color: #64748B; font-size: 11px;")
        header_row.addStretch()
        header_row.addWidget(self.footer_label)
        main_layout.addLayout(header_row)
        
        # ── OUTPUT PANE ──
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        # Output gets all the extra vertical space
        main_layout.addWidget(self.output_box, stretch=1)
        
        # ── INPUT CONTAINER ──
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #13161C; 
                border: 1px solid #2D3748; 
                border-radius: 12px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(12)
        
        # User Prompt
        self.usr_input = QTextEdit()
        self.usr_input.setMaximumHeight(60)
        self.usr_input.setPlaceholderText("Ask anything...")
        self.usr_input.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #E2E8F0;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.usr_input, stretch=1)
        
        # Actions Column (side by side inside the input pill)
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        
        self.btn_send = QPushButton("Send")
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #0F172A;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
            }
        """)
        self.btn_send.clicked.connect(self._on_send)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.setMinimumWidth(60)
        self.btn_send.setMaximumHeight(36)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_stop.setEnabled(False)
        self.btn_stop.hide()
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setMinimumWidth(60)
        self.btn_stop.setMaximumHeight(36)
        
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: #64748B; 
                border: none; 
                border-radius: 8px;
                font-size: 13px; 
                font-weight: 600; 
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: #1E2530;
                color: #E2E8F0;
            }
        """)
        self.btn_clear.clicked.connect(self._on_clear)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setMaximumHeight(36)
        
        action_row.addWidget(self.btn_clear)
        action_row.addWidget(self.btn_stop)
        action_row.addWidget(self.btn_send)
        
        # Align buttons to the bottom right of the text edit
        input_layout.addLayout(action_row)
        input_layout.setAlignment(action_row, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        # Center the input container horizontally
        input_wrapper = QHBoxLayout()
        input_wrapper.setContentsMargins(0, 0, 0, 0)
        input_wrapper.addStretch()
        
        input_container.setMinimumWidth(600)
        input_container.setMaximumWidth(800)
        input_wrapper.addWidget(input_container, stretch=1)
        
        input_wrapper.addStretch()
        
        main_layout.addLayout(input_wrapper)
        
    def _on_send(self):
        usr_txt = self.usr_input.toPlainText().strip()
        sys_txt = "" # Removed from UI
        
        if not usr_txt:
            return
            
        self.output_box.clear()
        
        # Add debugging feedback for the user
        self.output_box.append("<span style='color: #94A3B8; font-size: 12px;'><i>[System] Connecting to active model in memory...</i></span>")
        self.output_box.append("<span style='color: #94A3B8; font-size: 12px;'><i>[System] Message dispatched. Waiting for inference...</i></span><br><br>")
        
        self.footer_label.setText("Generating...")
        self.btn_send.setEnabled(False)
        self.btn_send.hide()
        self.btn_stop.setEnabled(True)
        self.btn_stop.show()
        
        # Start async stream via service
        self.current_task_id = self.service.stream_generation(
            session=self.session,
            system_prompt=sys_txt,
            user_prompt=usr_txt,
            params={"model": "test"}, # in a real app, read from model settings
            on_event=self._handle_event
        )
        
    def _on_stop(self):
        if self.current_task_id:
            self.service.cancel_task(self.current_task_id)
            self._reset_ui("Cancelled")
            
    def _on_clear(self):
        self.usr_input.clear()
        self.output_box.clear()
        self.footer_label.setText("Ready")
        
    def _handle_event(self, event: Any):
        if isinstance(event, GenerationStarted):
            pass # UI is already loading
        elif isinstance(event, TokenReceived):
            # Append token without a newline
            cursor = self.output_box.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(event.text)
            self.output_box.setTextCursor(cursor)
        elif isinstance(event, GenerationCompleted):
            self.footer_label.setText(f"Completed in {event.latency:.2f}s | Usage: {event.usage}")
            self._reset_ui(None)
        elif event.__class__.__name__ == "DiagnosticsUpdated":
            diags = event.diagnostics
            html = f"<div style='background-color:#0F111A; padding:8px; border-radius:4px; margin: 4px 0px;'><span style='color:#38BDF8; font-weight:bold;'>[Runtime Diagnostics]</span><br>" \
                   f"<span style='color:#94A3B8; font-size:12px;'>Engine: {diags.engine} ({diags.backend_version}) | " \
                   f"Context: {diags.actual_context}/{diags.requested_context} | " \
                   f"RAM: {diags.actual_memory_mb:.1f}MB | " \
                   f"Threads: {diags.thread_configuration}</span></div><br>"
            self.output_box.append(html)
        elif isinstance(event, GenerationFailed):
            self.footer_label.setText(f"Error: {event.error_message}")
            self.output_box.append(f"\n[ERROR: {event.error_type}]\n{event.error_message}")
            self._reset_ui(None)
            
    def _reset_ui(self, footer_msg):
        if footer_msg:
            self.footer_label.setText(footer_msg)
        self.btn_send.setEnabled(True)
        self.btn_send.show()
        self.btn_stop.setEnabled(False)
        self.btn_stop.hide()
        self.current_task_id = None
