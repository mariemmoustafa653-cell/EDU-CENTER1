const fs = require('fs');
const pdfParse = require('pdf-parse');
const logger = require('../utils/logger');

const extractPages = async (filePath, startPage, endPage) => {
    const dataBuffer = fs.readFileSync(filePath);

    const options = {
        pagerender: function (pageData) {
            return pageData.getTextContent().then((textContent) => {
                const text = textContent.items.map((item) => item.str).join(' ');
                // Explicitly append a form feed so pages can be split properly
                return text + '\f';
            });
        },
    };

    const data = await pdfParse(dataBuffer, options);
    const totalPages = data.numpages;

    if (startPage > totalPages) {
        const error = new Error(
            `start_page (${startPage}) exceeds total pages (${totalPages})`
        );
        error.statusCode = 400;
        throw error;
    }

    const adjustedEnd = Math.min(endPage, totalPages);
    const allText = data.text;
    const pages = allText.split(/\f/);

    const selectedPages = pages.slice(startPage - 1, adjustedEnd);
    const extractedText = selectedPages.join('\n');

    logger.info('PDF text extracted', {
        totalPages,
        requestedRange: `${startPage}-${endPage}`,
        actualRange: `${startPage}-${adjustedEnd}`,
        extractedLength: extractedText.length,
    });

    return extractedText;
};

module.exports = { extractPages };
