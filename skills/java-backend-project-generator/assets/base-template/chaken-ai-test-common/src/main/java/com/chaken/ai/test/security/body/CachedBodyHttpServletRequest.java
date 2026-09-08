package com.chaken.ai.test.security.body;

import jakarta.servlet.ReadListener;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class CachedBodyHttpServletRequest extends HttpServletRequestWrapper {
    private static final String FORM_CONTENT_TYPE = "application/x-www-form-urlencoded";

    private final byte[] body;
    private Map<String, String[]> formParameterMap;

    public CachedBodyHttpServletRequest(HttpServletRequest request, byte[] body) {
        super(request);
        this.body = body == null ? new byte[0] : body.clone();
    }

    public byte[] getCachedBody() {
        return body.clone();
    }

    @Override
    public ServletInputStream getInputStream() {
        ByteArrayInputStream inputStream = new ByteArrayInputStream(body);
        return new ServletInputStream() {
            @Override
            public boolean isFinished() {
                return inputStream.available() == 0;
            }

            @Override
            public boolean isReady() {
                return true;
            }

            @Override
            public void setReadListener(ReadListener readListener) {
                if (readListener == null) {
                    return;
                }
                try {
                    readListener.onDataAvailable();
                    if (isFinished()) {
                        readListener.onAllDataRead();
                    }
                } catch (IOException ex) {
                    readListener.onError(ex);
                }
            }

            @Override
            public int read() {
                return inputStream.read();
            }
        };
    }

    @Override
    public BufferedReader getReader() {
        Charset charset = getCharacterEncoding() == null
                ? StandardCharsets.UTF_8
                : Charset.forName(getCharacterEncoding());
        return new BufferedReader(new InputStreamReader(getInputStream(), charset));
    }

    @Override
    public String getParameter(String name) {
        String[] values = getParameterMap().get(name);
        return values == null || values.length == 0 ? null : values[0];
    }

    @Override
    public Map<String, String[]> getParameterMap() {
        if (!isFormUrlEncoded()) {
            return super.getParameterMap();
        }
        if (formParameterMap == null) {
            formParameterMap = parseFormParameterMap();
        }
        return formParameterMap;
    }

    @Override
    public Enumeration<String> getParameterNames() {
        return Collections.enumeration(getParameterMap().keySet());
    }

    @Override
    public String[] getParameterValues(String name) {
        return getParameterMap().get(name);
    }

    private boolean isFormUrlEncoded() {
        String contentType = getContentType();
        return contentType != null && contentType.toLowerCase().startsWith(FORM_CONTENT_TYPE);
    }

    private Map<String, String[]> parseFormParameterMap() {
        Map<String, List<String>> values = new LinkedHashMap<>();
        super.getParameterMap().forEach((key, existingValues) -> {
            List<String> list = values.computeIfAbsent(key, ignored -> new ArrayList<>());
            Collections.addAll(list, existingValues);
        });

        String formBody = new String(body, requestCharset());
        if (!formBody.isBlank()) {
            for (String pair : formBody.split("&")) {
                if (pair.isBlank()) {
                    continue;
                }
                int index = pair.indexOf('=');
                String key = decode(index < 0 ? pair : pair.substring(0, index));
                String value = decode(index < 0 ? "" : pair.substring(index + 1));
                values.computeIfAbsent(key, ignored -> new ArrayList<>()).add(value);
            }
        }

        Map<String, String[]> result = new LinkedHashMap<>();
        values.forEach((key, list) -> result.put(key, list.toArray(String[]::new)));
        return Collections.unmodifiableMap(result);
    }

    private String decode(String value) {
        return URLDecoder.decode(value, requestCharset());
    }

    private Charset requestCharset() {
        return getCharacterEncoding() == null
                ? StandardCharsets.UTF_8
                : Charset.forName(getCharacterEncoding());
    }
}
