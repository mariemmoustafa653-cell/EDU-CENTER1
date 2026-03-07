const multer = require('multer');
const path = require('path');
const os = require('os');
const config = require('./env');

const storage = multer.diskStorage({
    destination: os.tmpdir(),
    filename: (_req, file, cb) => {
        const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1e9)}${path.extname(file.originalname)}`;
        cb(null, uniqueName);
    },
});

const fileFilter = (_req, file, cb) => {
    if (file.mimetype !== 'application/pdf') {
        const error = new Error('Only PDF files are allowed');
        error.statusCode = 400;
        return cb(error, false);
    }
    cb(null, true);
};

const upload = multer({
    storage,
    fileFilter,
    limits: {
        fileSize: config.maxFileSizeMb * 1024 * 1024,
    },
});

module.exports = upload;
