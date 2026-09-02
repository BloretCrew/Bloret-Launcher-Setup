"""Blora Design 2.x semantic token names used by the Qt adapter.

PyQt cannot render Web Custom Elements or CSS cascade layers. The names remain
canonical here; the adapter maps them to Qt stylesheet values at render time.
"""

BLORA_TOKENS = {
    "surface_canvas": "--blora-color-surface-canvas",
    "surface_default": "--blora-color-surface-default",
    "text_primary": "--blora-color-text-primary",
    "text_secondary": "--blora-color-text-secondary",
    "text_muted": "--blora-color-text-muted",
    "action_primary": "--blora-color-action-primary-default",
    "action_hover": "--blora-color-action-primary-hover",
    "status_danger": "--blora-color-status-danger",
    "status_success": "--blora-color-status-success",
    "status_warning": "--blora-color-status-warning",
    "control_height": "--blora-control-height",
    "control_radius": "--blora-control-radius",
}

# Values are deliberately sourced from the semantic token names rather than 1.x APIs.
QT_TOKEN_VALUES = {
    BLORA_TOKENS["surface_canvas"]: "#fff8f5",
    BLORA_TOKENS["surface_default"]: "#ffffff",
    BLORA_TOKENS["text_primary"]: "#2b1713",
    BLORA_TOKENS["text_secondary"]: "#5d4037",
    BLORA_TOKENS["text_muted"]: "#806c66",
    BLORA_TOKENS["action_primary"]: "#c54b35",
    BLORA_TOKENS["action_hover"]: "#a83c2a",
    BLORA_TOKENS["status_danger"]: "#b3261e",
    BLORA_TOKENS["status_success"]: "#26734d",
    BLORA_TOKENS["status_warning"]: "#8a5a00",
}


def qt_stylesheet() -> str:
    return f"""
    QWidget {{ background: {QT_TOKEN_VALUES[BLORA_TOKENS['surface_canvas']]}; color: {QT_TOKEN_VALUES[BLORA_TOKENS['text_primary']]}; }}
    QFrame#card {{ background: {QT_TOKEN_VALUES[BLORA_TOKENS['surface_default']]}; border: 1px solid #ead8d2; border-radius: 10px; }}
    QPushButton {{ min-height: 36px; padding: 0 16px; border-radius: 8px; border: 1px solid #d7bdb5; }}
    QPushButton#primary {{ background: {QT_TOKEN_VALUES[BLORA_TOKENS['action_primary']]}; color: white; border: 0; }}
    QPushButton#primary:hover {{ background: {QT_TOKEN_VALUES[BLORA_TOKENS['action_hover']]}; }}
    QLineEdit {{ min-height: 34px; border: 1px solid #d7bdb5; border-radius: 8px; padding: 0 10px; background: white; }}
    QProgressBar {{ min-height: 12px; border: 0; border-radius: 6px; background: #f0dfd9; text-align: center; }}
    QProgressBar::chunk {{ background: {QT_TOKEN_VALUES[BLORA_TOKENS['action_primary']]}; border-radius: 6px; }}
    """
