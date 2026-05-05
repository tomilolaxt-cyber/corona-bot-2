"""
Generate app icons for Corona School Bot PWA
Run this script to create icon-192.png and icon-512.png in the static folder
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    
    def create_icon(size, filename):
        # Create image with red gradient background
        img = Image.new('RGB', (size, size), color='#dc143c')
        draw = ImageDraw.Draw(img)
        
        # Draw red gradient background
        for y in range(size):
            r = int(220 - (220-139) * y / size)
            g = int(20 - 20 * y / size)
            b = int(60 - 60 * y / size)
            draw.line([(0, y), (size, y)], fill=(r, g, b))
        
        # Draw white circle
        circle_radius = size // 3
        circle_bbox = [
            size//2 - circle_radius,
            size//2 - circle_radius,
            size//2 + circle_radius,
            size//2 + circle_radius
        ]
        draw.ellipse(circle_bbox, fill='white')
        
        # Draw text
        try:
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "🤖"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill='#dc143c', font=font)
        
        # Save
        img.save(f'static/{filename}')
        print(f'✅ Created static/{filename}')
    
    # Generate icons
    create_icon(192, 'icon-192.png')
    create_icon(512, 'icon-512.png')
    
    print('\n🎉 Icons generated successfully!')
    print('Your PWA is ready to be installed on iOS and Android!')
    
except ImportError:
    print('⚠️  Pillow library not found.')
    print('Install it with: pip install Pillow')
    print('\nOR use the create_icons.html file:')
    print('1. Open create_icons.html in your browser')
    print('2. Download both icons')
    print('3. Save them in the static folder')
