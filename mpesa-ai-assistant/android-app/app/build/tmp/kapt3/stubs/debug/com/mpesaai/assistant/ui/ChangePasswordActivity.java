package com.mpesaai.assistant.ui;

/**
 * Lets a signed-in user change their password directly, without going
 * through the WhatsApp reset-code flow. Requires the current password.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0000\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0012\u0010\u0003\u001a\u00020\u00042\b\u0010\u0005\u001a\u0004\u0018\u00010\u0006H\u0014J \u0010\u0007\u001a\u00020\u00042\u0006\u0010\b\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000b2\u0006\u0010\f\u001a\u00020\rH\u0002\u00a8\u0006\u000e"}, d2 = {"Lcom/mpesaai/assistant/ui/ChangePasswordActivity;", "Landroidx/appcompat/app/AppCompatActivity;", "()V", "onCreate", "", "savedInstanceState", "Landroid/os/Bundle;", "showStatus", "view", "Landroid/widget/TextView;", "message", "", "isError", "", "app_debug"})
public final class ChangePasswordActivity extends androidx.appcompat.app.AppCompatActivity {
    
    public ChangePasswordActivity() {
        super();
    }
    
    @java.lang.Override()
    protected void onCreate(@org.jetbrains.annotations.Nullable()
    android.os.Bundle savedInstanceState) {
    }
    
    private final void showStatus(android.widget.TextView view, java.lang.String message, boolean isError) {
    }
}