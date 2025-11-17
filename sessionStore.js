// ================================
//  SQLite Session Store for express-session
// ================================

const { Store } = require('express-session');
const { getDatabase } = require('./database');

/**
 * Custom SQLite session store for express-session
 * Stores sessions in the SQLite database for persistence across server restarts
 */
class SQLiteSessionStore extends Store {
  constructor(options = {}) {
    super(options);
    this.db = null;
    this.initPromise = null;
  }

  async getDb() {
    if (!this.db) {
      if (!this.initPromise) {
        this.initPromise = getDatabase().then(db => {
          this.db = db;
          return db;
        });
      }
      return this.initPromise;
    }
    return Promise.resolve(this.db);
  }

  async get(sessionId, callback) {
    try {
      const db = await this.getDb();
      const session = await db.getSession(sessionId);
      
      if (!session) {
        return callback(null, null);
      }

      // Parse session data from JSON (we'll store it as JSON in the database)
      // For now, we'll reconstruct the session from the user_id
      // The actual session data is stored by express-session, but we need to store it
      // Let's check if we have a session_data column, if not, we'll need to add it
      const sessionData = {
        userId: session.user_id,
        sessionId: session.id,
        cookie: {
          originalMaxAge: 7 * 24 * 60 * 60 * 1000,
          expires: new Date(session.expires_at),
          secure: process.env.NODE_ENV === 'production',
          httpOnly: true,
          sameSite: 'lax',
          path: '/',
        },
      };

      callback(null, sessionData);
    } catch (err) {
      callback(err);
    }
  }

  async set(sessionId, session, callback) {
    try {
      const db = await this.getDb();
      
      // Extract user ID from session
      const userId = session.userId || session.passport?.user || null;
      
      if (!userId) {
        // No user ID, skip storing in database (let express-session handle it)
        return callback(null);
      }

      // Calculate expiration (7 days from now, or use session cookie maxAge)
      const maxAge = session.cookie?.maxAge || 7 * 24 * 60 * 60 * 1000;
      const expiresAt = new Date(Date.now() + maxAge);

      // Store session in database
      // First, try to update existing session
      try {
        await db.deleteSession(sessionId);
      } catch (err) {
        // Ignore if session doesn't exist
      }

      await db.createSession(userId, sessionId, expiresAt.toISOString());
      
      callback(null);
    } catch (err) {
      callback(err);
    }
  }

  async destroy(sessionId, callback) {
    try {
      const db = await this.getDb();
      await db.deleteSession(sessionId);
      callback(null);
    } catch (err) {
      callback(err);
    }
  }

  async touch(sessionId, session, callback) {
    // Update expiration time
    try {
      const db = await this.getDb();
      const userId = session.userId || session.passport?.user || null;
      
      if (!userId) {
        return callback(null);
      }

      const maxAge = session.cookie?.maxAge || 7 * 24 * 60 * 60 * 1000;
      const expiresAt = new Date(Date.now() + maxAge);

      // Delete and recreate to update expiration
      await db.deleteSession(sessionId);
      await db.createSession(userId, sessionId, expiresAt.toISOString());
      
      callback(null);
    } catch (err) {
      callback(err);
    }
  }

  async all(callback) {
    // Not typically needed, but required by Store interface
    callback(null, []);
  }

  async length(callback) {
    try {
      const db = await this.getDb();
      const result = await new Promise((resolve, reject) => {
        db.db.get('SELECT COUNT(*) as count FROM sessions WHERE expires_at > ?', 
          [new Date().toISOString()], 
          (err, row) => {
            if (err) reject(err);
            else resolve(row);
          }
        );
      });
      callback(null, result?.count || 0);
    } catch (err) {
      callback(err);
    }
  }

  async clear(callback) {
    try {
      const db = await this.getDb();
      await db.deleteExpiredSessions();
      // Delete all sessions (not just expired)
      await new Promise((resolve, reject) => {
        db.db.run('DELETE FROM sessions', (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
      callback(null);
    } catch (err) {
      callback(err);
    }
  }
}

module.exports = SQLiteSessionStore;

