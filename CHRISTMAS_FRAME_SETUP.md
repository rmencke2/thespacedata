# Christmas Garland Frame Setup

## Adding the Christmas Garland Border Image

To use the Christmas garland image as a border for the Holiday Frame preset:

1. **Save the image:**
   - Save the Christmas garland image as `christmas-garland-frame.png`
   - Recommended size: 1920x200 or similar (wide horizontal garland)
   - Format: PNG with transparency (so the garland overlays on the video)

2. **Place the image:**
   - Create the directory if it doesn't exist: `mkdir -p assets/christmas`
   - Copy the image to: `assets/christmas/christmas-garland-frame.png`

3. **Verify:**
   - The Holiday Frame preset will automatically use this image when available
   - If the image is not found, it will fall back to a simple colored border
   - The garland will be placed on **top and bottom** of the video only

## Image Requirements

- **Format:** PNG (with transparency/alpha channel)
- **Recommended dimensions:** Wide horizontal garland (e.g., 1920x200, 1920x150, etc.)
- **Content:** Christmas garland that will be placed on top and bottom of videos
- **Transparency:** The background should be transparent so the video shows through
- **Aspect Ratio:** Wide horizontal format works best (the garland will be scaled to video width)

## Making the Garland Narrower

The garland height is currently set to **8% of the video height**. To adjust this:

1. **Edit the code:**
   - Open `services/christmasVideoService.js`
   - Find the line: `const garlandHeightPercent = 0.08;`
   - Change the value:
     - `0.05` = 5% of video height (narrower)
     - `0.08` = 8% of video height (current default)
     - `0.10` = 10% of video height
     - `0.15` = 15% of video height (wider)

2. **Or edit the image:**
   - Make your garland image narrower (reduce the height)
   - The system will scale it to match the video width
   - A narrower source image will result in a narrower overlay

## How It Works

- The garland image is scaled to match the video **width**
- It's then cropped to a height that's 8% of the video height
- One copy is placed at the **top** (y=0)
- Another copy is **flipped vertically** and placed at the **bottom**
- The original video orientation is preserved (no rotation)

## Testing

After adding the image, test the Holiday Frame preset:
1. Upload a video (max 20 seconds or 500MB)
2. Select "Holiday Frame" preset
3. Process the video
4. The garland should appear on the top and bottom of your video

