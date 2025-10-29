# Modern Portfolio Website

A modern, responsive portfolio website with a dark theme and neon blue accents. Built with HTML, CSS, and JavaScript.

## Features

- 🌙 Dark theme with neon blue accents
- 📱 Fully responsive design
- ✨ Smooth animations and transitions
- 🎯 Interactive navigation with scroll spy
- 💼 Project showcase section
- 📝 Working contact form
- 🎨 Modern UI/UX design

## Technologies Used

- HTML5
- CSS3 (with CSS Variables and Flexbox/Grid)
- JavaScript (ES6+)
- AOS (Animate On Scroll) library
- Font Awesome icons

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/portfolio-website.git
```

2. Navigate to the project directory:
```bash
cd portfolio-website
```

3. Open `index.html` in your browser or use a local development server:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve
```

4. Visit `http://localhost:8000` (or the appropriate port) in your browser.

## Customization

### Colors
The color scheme can be customized in the `styles/main.css` file:

```css
:root {
    --primary-color: #00f7ff;
    --primary-glow: 0 0 10px rgba(0, 247, 255, 0.5);
    --background-dark: #0a192f;
    --background-darker: #060d1a;
    --text-primary: #ffffff;
    --text-secondary: #8892b0;
}
```

### Content
- Update the personal information in `index.html`
- Replace project images in the `assets/images` directory
- Modify social media links in the hero section
- Update the contact form handling in `js/main.js`

## Project Structure

```
portfolio-website/
├── index.html
├── styles/
│   └── main.css
├── js/
│   └── main.js
├── assets/
│   └── images/
│       ├── profile.jpg
│       ├── project1.jpg
│       └── project2.jpg
└── README.md
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Font Awesome for the icons
- AOS library for scroll animations
- Inspiration from modern portfolio designs 