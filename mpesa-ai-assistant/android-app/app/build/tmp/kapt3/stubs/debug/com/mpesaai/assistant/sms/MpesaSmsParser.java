package com.mpesaai.assistant.sms;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0010\u0010\b\u001a\u00020\t2\b\u0010\n\u001a\u0004\u0018\u00010\u000bJ\u0010\u0010\f\u001a\u0004\u0018\u00010\r2\u0006\u0010\u000e\u001a\u00020\u000bJ\u001c\u0010\u000f\u001a\u000e\u0012\u0004\u0012\u00020\u000b\u0012\u0004\u0012\u00020\u000b0\u00102\u0006\u0010\u0011\u001a\u00020\u000bH\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0012"}, d2 = {"Lcom/mpesaai/assistant/sms/MpesaSmsParser;", "", "()V", "AMOUNT_REGEX", "Lkotlin/text/Regex;", "BALANCE_REGEX", "CODE_REGEX", "DATE_TIME_REGEX", "isMpesaSender", "", "sender", "", "parse", "Lcom/mpesaai/assistant/sms/ParsedTransaction;", "body", "parseDateTime", "Lkotlin/Pair;", "text", "app_debug"})
public final class MpesaSmsParser {
    @org.jetbrains.annotations.NotNull()
    private static final kotlin.text.Regex CODE_REGEX = null;
    @org.jetbrains.annotations.NotNull()
    private static final kotlin.text.Regex AMOUNT_REGEX = null;
    @org.jetbrains.annotations.NotNull()
    private static final kotlin.text.Regex BALANCE_REGEX = null;
    @org.jetbrains.annotations.NotNull()
    private static final kotlin.text.Regex DATE_TIME_REGEX = null;
    @org.jetbrains.annotations.NotNull()
    public static final com.mpesaai.assistant.sms.MpesaSmsParser INSTANCE = null;
    
    private MpesaSmsParser() {
        super();
    }
    
    public final boolean isMpesaSender(@org.jetbrains.annotations.Nullable()
    java.lang.String sender) {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.mpesaai.assistant.sms.ParsedTransaction parse(@org.jetbrains.annotations.NotNull()
    java.lang.String body) {
        return null;
    }
    
    private final kotlin.Pair<java.lang.String, java.lang.String> parseDateTime(java.lang.String text) {
        return null;
    }
}