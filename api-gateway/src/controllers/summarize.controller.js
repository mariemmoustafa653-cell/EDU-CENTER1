const { extractPages } = require('../services/pdf-extractor');
const { cleanText } = require('../services/text-cleaner');
const { summarize } = require('../services/nlp-client');
const { deleteFile } = require('../utils/file-cleanup');
const logger = require('../utils/logger');

const handleSummarize = async (req, res, next) => {
    const { file } = req;
    const startPage = parseInt(req.body.start_page, 10);
    const endPage = parseInt(req.body.end_page, 10);

    try {
        if (!file) {
            const error = new Error('PDF file is required');
            error.statusCode = 400;
            throw error;
        }

        logger.info('Summarization started', {
            requestId: req.id,
            fileName: file.originalname,
            fileSize: file.size,
            startPage,
            endPage,
        });

        const rawText = await extractPages(file.path, startPage, endPage);
        const cleanedText = cleanText(rawText);

        if (!cleanedText.length) {
            const error = new Error('No text found in selected pages');
            error.statusCode = 422;
            throw error;
        }

        const result = await summarize(cleanedText, req.id);

        logger.info('Summarization completed', {
            requestId: req.id,
            originalLength: result.original_length,
            summaryLength: result.summary_length,
        });

        res.json({
            status: 'success',
            request_id: req.id,
            ...result,
        });
    } catch (error) {
        next(error);
    } finally {
        deleteFile(file?.path);
    }
};

module.exports = { handleSummarize };
