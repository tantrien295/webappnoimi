-- Thêm dữ liệu mặc định cho bảng settings
INSERT INTO public.settings (
    company_name,
    company_logo_url,
    primary_color,
    secondary_color,
    welcome_title,
    welcome_subtitle,
    footer_text,
    contact_email,
    contact_phone,
    contact_address,
    facebook_url,
    instagram_url,
    twitter_url,
    created_at,
    updated_at
) VALUES (
    'Salon Beauty',
    '/static/images/logo.png',
    '#4A90E2',
    '#F5A623',
    'Chào mừng đến với Salon Beauty',
    'Nơi làm đẹp của bạn',
    '© 2024 Salon Beauty. All rights reserved.',
    'contact@salonbeauty.com',
    '0123456789',
    '123 Đường ABC, Quận XYZ, TP.HCM',
    'https://facebook.com/salonbeauty',
    'https://instagram.com/salonbeauty',
    'https://twitter.com/salonbeauty',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
); 