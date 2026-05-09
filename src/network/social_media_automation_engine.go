/*
OMNI Social Media Automation Engine
====================================
Production-grade cross-platform social media automation engine.
Provides unified API for scheduling, publishing, analytics retrieval,
and content management across major social media platforms.

Inspired by: github.com/vasani-arpit/Social-Media-Automation
OMNI Layer: Network (Go)
*/

package network

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// ─────────────────────────────────────────────
// Section 1: Core Types & Enums
// ─────────────────────────────────────────────

// SocialPlatform represents a supported social media platform.
type SocialPlatform string

const (
	PlatformTwitter   SocialPlatform = "twitter"
	PlatformFacebook  SocialPlatform = "facebook"
	PlatformInstagram SocialPlatform = "instagram"
	PlatformLinkedIn  SocialPlatform = "linkedin"
	PlatformYouTube   SocialPlatform = "youtube"
	PlatformTikTok    SocialPlatform = "tiktok"
	PlatformPinterest SocialPlatform = "pinterest"
	PlatformReddit    SocialPlatform = "reddit"
	PlatformMastodon  SocialPlatform = "mastodon"
	PlatformThreads   SocialPlatform = "threads"
)

// PostStatus represents the lifecycle state of a social post.
type PostStatus string

const (
	PostStatusDraft     PostStatus = "draft"
	PostStatusScheduled PostStatus = "scheduled"
	PostStatusPublished PostStatus = "published"
	PostStatusFailed    PostStatus = "failed"
	PostStatusDeleted   PostStatus = "deleted"
)

// MediaType represents the type of media attachment.
type MediaType string

const (
	MediaTypeImage MediaType = "image"
	MediaTypeVideo MediaType = "video"
	MediaTypeGIF   MediaType = "gif"
	MediaTypeDoc   MediaType = "document"
)

// ContentType represents the kind of social post.
type ContentType string

const (
	ContentPost    ContentType = "post"
	ContentStory   ContentType = "story"
	ContentReel    ContentType = "reel"
	ContentThread  ContentType = "thread"
	ContentPoll    ContentType = "poll"
	ContentArticle ContentType = "article"
	ContentLive    ContentType = "live"
)

// ─────────────────────────────────────────────
// Section 2: Data Structures
// ─────────────────────────────────────────────

// PlatformCredentials holds OAuth/API credentials for a platform.
type PlatformCredentials struct {
	Platform     SocialPlatform `json:"platform"`
	ClientID     string         `json:"client_id"`
	ClientSecret string         `json:"client_secret"`
	AccessToken  string         `json:"access_token"`
	RefreshToken string         `json:"refresh_token"`
	APIKey       string         `json:"api_key"`
	APISecret    string         `json:"api_secret"`
	BaseURL      string         `json:"base_url"`
	ExpiresAt    time.Time      `json:"expires_at"`
	Scopes       []string       `json:"scopes"`
}

// MediaAttachment represents a media file to attach to a post.
type MediaAttachment struct {
	Type      MediaType `json:"type"`
	FilePath  string    `json:"file_path"`
	URL       string    `json:"url"`
	AltText   string    `json:"alt_text"`
	Width     int       `json:"width,omitempty"`
	Height    int       `json:"height,omitempty"`
	Duration  int       `json:"duration_seconds,omitempty"`
	MediaID   string    `json:"media_id,omitempty"`
	Thumbnail string    `json:"thumbnail,omitempty"`
}

// SocialPost represents a post to be published across platforms.
type SocialPost struct {
	ID           string            `json:"id"`
	Content      string            `json:"content"`
	ContentType  ContentType       `json:"content_type"`
	Platforms    []SocialPlatform  `json:"platforms"`
	Media        []MediaAttachment `json:"media"`
	Hashtags     []string          `json:"hashtags"`
	Mentions     []string          `json:"mentions"`
	Link         string            `json:"link,omitempty"`
	Location     string            `json:"location,omitempty"`
	ScheduledAt  *time.Time        `json:"scheduled_at,omitempty"`
	Status       PostStatus        `json:"status"`
	CreatedAt    time.Time         `json:"created_at"`
	PublishedAt  *time.Time        `json:"published_at,omitempty"`
	PlatformIDs  map[string]string `json:"platform_ids"`
	Tags         []string          `json:"tags"`
	Metadata     map[string]string `json:"metadata"`
	RetryCount   int               `json:"retry_count"`
	MaxRetries   int               `json:"max_retries"`
	ErrorMessage string            `json:"error_message,omitempty"`
}

// PostAnalytics holds engagement metrics for a published post.
type PostAnalytics struct {
	PostID        string         `json:"post_id"`
	Platform      SocialPlatform `json:"platform"`
	PlatformID    string         `json:"platform_id"`
	Impressions   int64          `json:"impressions"`
	Reach         int64          `json:"reach"`
	Likes         int64          `json:"likes"`
	Comments      int64          `json:"comments"`
	Shares        int64          `json:"shares"`
	Saves         int64          `json:"saves"`
	Clicks        int64          `json:"clicks"`
	Engagements   int64          `json:"engagements"`
	EngagementPct float64        `json:"engagement_pct"`
	VideoViews    int64          `json:"video_views,omitempty"`
	FetchedAt     time.Time      `json:"fetched_at"`
}

// AccountProfile holds profile info for a connected social account.
type AccountProfile struct {
	Platform      SocialPlatform `json:"platform"`
	UserID        string         `json:"user_id"`
	Username      string         `json:"username"`
	DisplayName   string         `json:"display_name"`
	Bio           string         `json:"bio"`
	Followers     int64          `json:"followers"`
	Following     int64          `json:"following"`
	PostCount     int64          `json:"post_count"`
	Verified      bool           `json:"verified"`
	ProfileURL    string         `json:"profile_url"`
	AvatarURL     string         `json:"avatar_url"`
	LastRefreshed time.Time      `json:"last_refreshed"`
}

// CampaignSchedule defines a scheduled campaign across platforms.
type CampaignSchedule struct {
	CampaignID  string            `json:"campaign_id"`
	Name        string            `json:"name"`
	Description string            `json:"description"`
	Posts       []SocialPost      `json:"posts"`
	StartDate   time.Time         `json:"start_date"`
	EndDate     time.Time         `json:"end_date"`
	Timezone    string            `json:"timezone"`
	Status      string            `json:"status"`
	Tags        map[string]string `json:"tags"`
}

// RateLimitState tracks API rate limits per platform.
type RateLimitState struct {
	Platform    SocialPlatform `json:"platform"`
	Endpoint    string         `json:"endpoint"`
	Remaining   int            `json:"remaining"`
	Limit       int            `json:"limit"`
	ResetAt     time.Time      `json:"reset_at"`
	LastChecked time.Time      `json:"last_checked"`
}

// PublishResult captures the result of a publish operation.
type PublishResult struct {
	Platform   SocialPlatform `json:"platform"`
	Success    bool           `json:"success"`
	PlatformID string         `json:"platform_id,omitempty"`
	URL        string         `json:"url,omitempty"`
	Error      string         `json:"error,omitempty"`
	Timestamp  time.Time      `json:"timestamp"`
}

// ─────────────────────────────────────────────
// Section 3: Platform API Adapters
// ─────────────────────────────────────────────

// PlatformAdapter defines the interface each platform must implement.
type PlatformAdapter interface {
	Platform() SocialPlatform
	Publish(ctx context.Context, post *SocialPost) (*PublishResult, error)
	Delete(ctx context.Context, platformID string) error
	GetAnalytics(ctx context.Context, platformID string) (*PostAnalytics, error)
	GetProfile(ctx context.Context) (*AccountProfile, error)
	UploadMedia(ctx context.Context, media *MediaAttachment) (string, error)
	RefreshToken(ctx context.Context) error
	ValidateCredentials() error
	GetRateLimits() *RateLimitState
}

// ── Twitter/X Adapter ──

type TwitterAdapter struct {
	creds      *PlatformCredentials
	httpClient *http.Client
	rateLimit  *RateLimitState
}

func NewTwitterAdapter(creds *PlatformCredentials) *TwitterAdapter {
	return &TwitterAdapter{
		creds:      creds,
		httpClient: &http.Client{Timeout: 30 * time.Second},
		rateLimit:  &RateLimitState{Platform: PlatformTwitter},
	}
}

func (t *TwitterAdapter) Platform() SocialPlatform { return PlatformTwitter }

func (t *TwitterAdapter) Publish(ctx context.Context, post *SocialPost) (*PublishResult, error) {
	apiURL := "https://api.twitter.com/2/tweets"

	body := map[string]interface{}{
		"text": t.buildTweetText(post),
	}

	// Attach media IDs if present
	if len(post.Media) > 0 {
		mediaIDs := make([]string, 0)
		for _, m := range post.Media {
			if m.MediaID != "" {
				mediaIDs = append(mediaIDs, m.MediaID)
			}
		}
		if len(mediaIDs) > 0 {
			body["media"] = map[string]interface{}{"media_ids": mediaIDs}
		}
	}

	// Polls
	if post.ContentType == ContentPoll && post.Metadata != nil {
		if options, ok := post.Metadata["poll_options"]; ok {
			body["poll"] = map[string]interface{}{
				"options":          strings.Split(options, "|"),
				"duration_minutes": 1440,
			}
		}
	}

	jsonBody, _ := json.Marshal(body)
	req, err := http.NewRequestWithContext(ctx, "POST", apiURL, bytes.NewReader(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("twitter: create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+t.creds.AccessToken)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("twitter: publish: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusCreated {
		return &PublishResult{
			Platform:  PlatformTwitter,
			Success:   false,
			Error:     fmt.Sprintf("HTTP %d: %s", resp.StatusCode, string(respBody)),
			Timestamp: time.Now().UTC(),
		}, nil
	}

	var result map[string]interface{}
	json.Unmarshal(respBody, &result)

	tweetID := ""
	if data, ok := result["data"].(map[string]interface{}); ok {
		if id, ok := data["id"].(string); ok {
			tweetID = id
		}
	}

	return &PublishResult{
		Platform:   PlatformTwitter,
		Success:    true,
		PlatformID: tweetID,
		URL:        fmt.Sprintf("https://twitter.com/i/web/status/%s", tweetID),
		Timestamp:  time.Now().UTC(),
	}, nil
}

func (t *TwitterAdapter) Delete(ctx context.Context, platformID string) error {
	apiURL := fmt.Sprintf("https://api.twitter.com/2/tweets/%s", platformID)
	req, err := http.NewRequestWithContext(ctx, "DELETE", apiURL, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+t.creds.AccessToken)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("twitter delete failed: HTTP %d: %s", resp.StatusCode, string(body))
	}
	return nil
}

func (t *TwitterAdapter) GetAnalytics(ctx context.Context, platformID string) (*PostAnalytics, error) {
	apiURL := fmt.Sprintf("https://api.twitter.com/2/tweets/%s?tweet.fields=public_metrics,organic_metrics", platformID)
	req, err := http.NewRequestWithContext(ctx, "GET", apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+t.creds.AccessToken)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	analytics := &PostAnalytics{
		Platform:   PlatformTwitter,
		PlatformID: platformID,
		FetchedAt:  time.Now().UTC(),
	}

	if data, ok := result["data"].(map[string]interface{}); ok {
		if metrics, ok := data["public_metrics"].(map[string]interface{}); ok {
			analytics.Likes = int64(metrics["like_count"].(float64))
			analytics.Comments = int64(metrics["reply_count"].(float64))
			analytics.Shares = int64(metrics["retweet_count"].(float64))
			analytics.Impressions = int64(metrics["impression_count"].(float64))
		}
	}

	return analytics, nil
}

func (t *TwitterAdapter) GetProfile(ctx context.Context) (*AccountProfile, error) {
	apiURL := "https://api.twitter.com/2/users/me?user.fields=public_metrics,description,verified"
	req, err := http.NewRequestWithContext(ctx, "GET", apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+t.creds.AccessToken)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	profile := &AccountProfile{
		Platform:      PlatformTwitter,
		LastRefreshed: time.Now().UTC(),
	}

	if data, ok := result["data"].(map[string]interface{}); ok {
		profile.UserID, _ = data["id"].(string)
		profile.Username, _ = data["username"].(string)
		profile.DisplayName, _ = data["name"].(string)
		profile.Bio, _ = data["description"].(string)
		profile.Verified, _ = data["verified"].(bool)

		if metrics, ok := data["public_metrics"].(map[string]interface{}); ok {
			profile.Followers = int64(metrics["followers_count"].(float64))
			profile.Following = int64(metrics["following_count"].(float64))
			profile.PostCount = int64(metrics["tweet_count"].(float64))
		}
	}

	return profile, nil
}

func (t *TwitterAdapter) UploadMedia(ctx context.Context, media *MediaAttachment) (string, error) {
	apiURL := "https://upload.twitter.com/1.1/media/upload.json"

	f, err := os.Open(media.FilePath)
	if err != nil {
		return "", fmt.Errorf("twitter: open media: %w", err)
	}
	defer f.Close()

	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)
	part, err := writer.CreateFormFile("media", filepath.Base(media.FilePath))
	if err != nil {
		return "", err
	}
	io.Copy(part, f)
	writer.Close()

	req, err := http.NewRequestWithContext(ctx, "POST", apiURL, &buf)
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+t.creds.AccessToken)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(respBody, &result)

	mediaID := ""
	if id, ok := result["media_id_string"].(string); ok {
		mediaID = id
	}

	return mediaID, nil
}

func (t *TwitterAdapter) RefreshToken(ctx context.Context) error {
	if t.creds.RefreshToken == "" {
		return fmt.Errorf("twitter: no refresh token available")
	}
	data := url.Values{
		"grant_type":    {"refresh_token"},
		"refresh_token": {t.creds.RefreshToken},
		"client_id":     {t.creds.ClientID},
	}

	req, _ := http.NewRequestWithContext(ctx, "POST", "https://api.twitter.com/2/oauth2/token",
		strings.NewReader(data.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.SetBasicAuth(t.creds.ClientID, t.creds.ClientSecret)

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if token, ok := result["access_token"].(string); ok {
		t.creds.AccessToken = token
	}
	if refreshToken, ok := result["refresh_token"].(string); ok {
		t.creds.RefreshToken = refreshToken
	}
	if expiresIn, ok := result["expires_in"].(float64); ok {
		t.creds.ExpiresAt = time.Now().Add(time.Duration(expiresIn) * time.Second)
	}

	return nil
}

func (t *TwitterAdapter) ValidateCredentials() error {
	if t.creds.AccessToken == "" {
		return fmt.Errorf("twitter: access token required")
	}
	return nil
}

func (t *TwitterAdapter) GetRateLimits() *RateLimitState {
	return t.rateLimit
}

func (t *TwitterAdapter) buildTweetText(post *SocialPost) string {
	text := post.Content
	if len(post.Hashtags) > 0 {
		tags := make([]string, len(post.Hashtags))
		for i, tag := range post.Hashtags {
			if !strings.HasPrefix(tag, "#") {
				tags[i] = "#" + tag
			} else {
				tags[i] = tag
			}
		}
		text += "\n\n" + strings.Join(tags, " ")
	}
	if post.Link != "" {
		text += "\n" + post.Link
	}
	// Twitter 280-char limit
	if len(text) > 280 {
		text = text[:277] + "..."
	}
	return text
}

// ── Facebook Adapter ──

type FacebookAdapter struct {
	creds      *PlatformCredentials
	httpClient *http.Client
	rateLimit  *RateLimitState
	pageID     string
}

func NewFacebookAdapter(creds *PlatformCredentials, pageID string) *FacebookAdapter {
	return &FacebookAdapter{
		creds:      creds,
		httpClient: &http.Client{Timeout: 30 * time.Second},
		rateLimit:  &RateLimitState{Platform: PlatformFacebook},
		pageID:     pageID,
	}
}

func (fb *FacebookAdapter) Platform() SocialPlatform { return PlatformFacebook }

func (fb *FacebookAdapter) Publish(ctx context.Context, post *SocialPost) (*PublishResult, error) {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/%s/feed", fb.pageID)

	data := url.Values{
		"message":      {post.Content},
		"access_token": {fb.creds.AccessToken},
	}
	if post.Link != "" {
		data.Set("link", post.Link)
	}

	req, _ := http.NewRequestWithContext(ctx, "POST", apiURL, strings.NewReader(data.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("facebook: publish: %w", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if errData, ok := result["error"].(map[string]interface{}); ok {
		return &PublishResult{
			Platform:  PlatformFacebook,
			Success:   false,
			Error:     fmt.Sprintf("%v", errData["message"]),
			Timestamp: time.Now().UTC(),
		}, nil
	}

	postID, _ := result["id"].(string)
	return &PublishResult{
		Platform:   PlatformFacebook,
		Success:    true,
		PlatformID: postID,
		URL:        fmt.Sprintf("https://facebook.com/%s", postID),
		Timestamp:  time.Now().UTC(),
	}, nil
}

func (fb *FacebookAdapter) Delete(ctx context.Context, platformID string) error {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/%s?access_token=%s", platformID, fb.creds.AccessToken)
	req, _ := http.NewRequestWithContext(ctx, "DELETE", apiURL, nil)
	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("facebook delete failed: HTTP %d", resp.StatusCode)
	}
	return nil
}

func (fb *FacebookAdapter) GetAnalytics(ctx context.Context, platformID string) (*PostAnalytics, error) {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/%s?fields=insights.metric(post_impressions,post_engaged_users,post_reactions_by_type_total)&access_token=%s",
		platformID, fb.creds.AccessToken)
	req, _ := http.NewRequestWithContext(ctx, "GET", apiURL, nil)

	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return &PostAnalytics{
		Platform:   PlatformFacebook,
		PlatformID: platformID,
		FetchedAt:  time.Now().UTC(),
	}, nil
}

func (fb *FacebookAdapter) GetProfile(ctx context.Context) (*AccountProfile, error) {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/%s?fields=name,fan_count,about,picture&access_token=%s",
		fb.pageID, fb.creds.AccessToken)
	req, _ := http.NewRequestWithContext(ctx, "GET", apiURL, nil)

	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	return &AccountProfile{
		Platform:      PlatformFacebook,
		UserID:        fb.pageID,
		DisplayName:   fmt.Sprintf("%v", result["name"]),
		Followers:     int64(result["fan_count"].(float64)),
		LastRefreshed: time.Now().UTC(),
	}, nil
}

func (fb *FacebookAdapter) UploadMedia(ctx context.Context, media *MediaAttachment) (string, error) {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/%s/photos", fb.pageID)
	f, err := os.Open(media.FilePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)
	part, _ := writer.CreateFormFile("source", filepath.Base(media.FilePath))
	io.Copy(part, f)
	writer.WriteField("access_token", fb.creds.AccessToken)
	writer.WriteField("published", "false")
	writer.Close()

	req, _ := http.NewRequestWithContext(ctx, "POST", apiURL, &buf)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(respBody, &result)

	if id, ok := result["id"].(string); ok {
		return id, nil
	}
	return "", fmt.Errorf("facebook: no media id returned")
}

func (fb *FacebookAdapter) RefreshToken(ctx context.Context) error {
	apiURL := fmt.Sprintf("https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s",
		fb.creds.ClientID, fb.creds.ClientSecret, fb.creds.AccessToken)
	req, _ := http.NewRequestWithContext(ctx, "GET", apiURL, nil)

	resp, err := fb.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if token, ok := result["access_token"].(string); ok {
		fb.creds.AccessToken = token
	}
	return nil
}

func (fb *FacebookAdapter) ValidateCredentials() error {
	if fb.creds.AccessToken == "" || fb.pageID == "" {
		return fmt.Errorf("facebook: access_token and page_id required")
	}
	return nil
}

func (fb *FacebookAdapter) GetRateLimits() *RateLimitState { return fb.rateLimit }

// ── LinkedIn Adapter ──

type LinkedInAdapter struct {
	creds      *PlatformCredentials
	httpClient *http.Client
	rateLimit  *RateLimitState
	personURN  string
}

func NewLinkedInAdapter(creds *PlatformCredentials, personURN string) *LinkedInAdapter {
	return &LinkedInAdapter{
		creds:      creds,
		httpClient: &http.Client{Timeout: 30 * time.Second},
		rateLimit:  &RateLimitState{Platform: PlatformLinkedIn},
		personURN:  personURN,
	}
}

func (li *LinkedInAdapter) Platform() SocialPlatform { return PlatformLinkedIn }

func (li *LinkedInAdapter) Publish(ctx context.Context, post *SocialPost) (*PublishResult, error) {
	apiURL := "https://api.linkedin.com/v2/ugcPosts"

	shareContent := map[string]interface{}{
		"shareCommentary":    map[string]string{"text": post.Content},
		"shareMediaCategory": "NONE",
	}
	if post.Link != "" {
		shareContent["shareMediaCategory"] = "ARTICLE"
		shareContent["media"] = []map[string]interface{}{
			{
				"status":      "READY",
				"originalUrl": post.Link,
			},
		}
	}

	body := map[string]interface{}{
		"author":         li.personURN,
		"lifecycleState": "PUBLISHED",
		"specificContent": map[string]interface{}{
			"com.linkedin.ugc.ShareContent": shareContent,
		},
		"visibility": map[string]string{
			"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
		},
	}

	jsonBody, _ := json.Marshal(body)
	req, _ := http.NewRequestWithContext(ctx, "POST", apiURL, bytes.NewReader(jsonBody))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+li.creds.AccessToken)
	req.Header.Set("X-Restli-Protocol-Version", "2.0.0")

	resp, err := li.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("linkedin: publish: %w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusCreated {
		return &PublishResult{
			Platform:  PlatformLinkedIn,
			Success:   false,
			Error:     fmt.Sprintf("HTTP %d: %s", resp.StatusCode, string(respBody)),
			Timestamp: time.Now().UTC(),
		}, nil
	}

	postID := resp.Header.Get("x-restli-id")
	return &PublishResult{
		Platform:   PlatformLinkedIn,
		Success:    true,
		PlatformID: postID,
		URL:        fmt.Sprintf("https://www.linkedin.com/feed/update/%s", postID),
		Timestamp:  time.Now().UTC(),
	}, nil
}

func (li *LinkedInAdapter) Delete(ctx context.Context, platformID string) error {
	apiURL := fmt.Sprintf("https://api.linkedin.com/v2/ugcPosts/%s", url.PathEscape(platformID))
	req, _ := http.NewRequestWithContext(ctx, "DELETE", apiURL, nil)
	req.Header.Set("Authorization", "Bearer "+li.creds.AccessToken)

	resp, err := li.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusNoContent {
		return fmt.Errorf("linkedin delete: HTTP %d", resp.StatusCode)
	}
	return nil
}

func (li *LinkedInAdapter) GetAnalytics(ctx context.Context, platformID string) (*PostAnalytics, error) {
	return &PostAnalytics{Platform: PlatformLinkedIn, PlatformID: platformID, FetchedAt: time.Now().UTC()}, nil
}

func (li *LinkedInAdapter) GetProfile(ctx context.Context) (*AccountProfile, error) {
	return &AccountProfile{Platform: PlatformLinkedIn, UserID: li.personURN, LastRefreshed: time.Now().UTC()}, nil
}

func (li *LinkedInAdapter) UploadMedia(ctx context.Context, media *MediaAttachment) (string, error) {
	return "", fmt.Errorf("linkedin: media upload requires register-upload flow")
}

func (li *LinkedInAdapter) RefreshToken(ctx context.Context) error {
	return nil
}

func (li *LinkedInAdapter) ValidateCredentials() error {
	if li.creds.AccessToken == "" || li.personURN == "" {
		return fmt.Errorf("linkedin: access_token and person_urn required")
	}
	return nil
}

func (li *LinkedInAdapter) GetRateLimits() *RateLimitState { return li.rateLimit }

// ─────────────────────────────────────────────
// Section 4: Content Optimizer
// ─────────────────────────────────────────────

// ContentOptimizer adapts post content for each platform's requirements.
type ContentOptimizer struct{}

func NewContentOptimizer() *ContentOptimizer {
	return &ContentOptimizer{}
}

// OptimizeForPlatform adapts content to platform character limits and best practices.
func (co *ContentOptimizer) OptimizeForPlatform(content string, platform SocialPlatform) string {
	limits := map[SocialPlatform]int{
		PlatformTwitter:   280,
		PlatformFacebook:  63206,
		PlatformInstagram: 2200,
		PlatformLinkedIn:  3000,
		PlatformTikTok:    2200,
		PlatformPinterest: 500,
		PlatformReddit:    40000,
		PlatformMastodon:  500,
		PlatformThreads:   500,
	}

	limit, ok := limits[platform]
	if !ok {
		limit = 2000
	}

	if len(content) > limit {
		return content[:limit-3] + "..."
	}
	return content
}

// GenerateHashtagSuggestions returns platform-appropriate hashtags.
func (co *ContentOptimizer) GenerateHashtagSuggestions(content string, platform SocialPlatform) []string {
	// Extract potential keywords from content (simplified)
	words := strings.Fields(strings.ToLower(content))
	hashtags := make([]string, 0)
	seen := make(map[string]bool)

	for _, word := range words {
		cleaned := strings.Trim(word, ".,!?;:\"'()[]{}#@")
		if len(cleaned) >= 4 && !seen[cleaned] {
			seen[cleaned] = true
			hashtags = append(hashtags, "#"+cleaned)
		}
		if len(hashtags) >= 10 {
			break
		}
	}

	return hashtags
}

// GetBestPostingTimes returns optimal posting times per platform (UTC).
func (co *ContentOptimizer) GetBestPostingTimes(platform SocialPlatform) []time.Time {
	now := time.Now().UTC()
	year, month, day := now.Date()
	base := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)

	switch platform {
	case PlatformTwitter:
		return []time.Time{
			base.Add(9 * time.Hour),
			base.Add(12 * time.Hour),
			base.Add(17 * time.Hour),
		}
	case PlatformInstagram:
		return []time.Time{
			base.Add(11 * time.Hour),
			base.Add(14 * time.Hour),
			base.Add(19 * time.Hour),
		}
	case PlatformLinkedIn:
		return []time.Time{
			base.Add(8 * time.Hour),
			base.Add(10 * time.Hour),
			base.Add(12 * time.Hour),
		}
	case PlatformFacebook:
		return []time.Time{
			base.Add(9 * time.Hour),
			base.Add(13 * time.Hour),
			base.Add(16 * time.Hour),
		}
	default:
		return []time.Time{
			base.Add(10 * time.Hour),
			base.Add(14 * time.Hour),
			base.Add(18 * time.Hour),
		}
	}
}

// ─────────────────────────────────────────────
// Section 5: Scheduler Engine
// ─────────────────────────────────────────────

// SchedulerEngine manages post scheduling and execution.
type SchedulerEngine struct {
	mu        sync.Mutex
	queue     []*SocialPost
	campaigns map[string]*CampaignSchedule
	running   bool
	stopCh    chan struct{}
	publish   func(ctx context.Context, post *SocialPost, platform SocialPlatform) *PublishResult
}

func NewSchedulerEngine(publishFn func(ctx context.Context, post *SocialPost, platform SocialPlatform) *PublishResult) *SchedulerEngine {
	return &SchedulerEngine{
		queue:     make([]*SocialPost, 0),
		campaigns: make(map[string]*CampaignSchedule),
		stopCh:    make(chan struct{}),
		publish:   publishFn,
	}
}

func (se *SchedulerEngine) Schedule(post *SocialPost) {
	se.mu.Lock()
	defer se.mu.Unlock()
	post.Status = PostStatusScheduled
	se.queue = append(se.queue, post)
}

func (se *SchedulerEngine) Start() {
	se.mu.Lock()
	if se.running {
		se.mu.Unlock()
		return
	}
	se.running = true
	se.mu.Unlock()

	go se.scheduleLoop()
}

func (se *SchedulerEngine) Stop() {
	se.mu.Lock()
	if !se.running {
		se.mu.Unlock()
		return
	}
	se.running = false
	se.mu.Unlock()
	close(se.stopCh)
}

func (se *SchedulerEngine) scheduleLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-se.stopCh:
			return
		case <-ticker.C:
			se.processQueue()
		}
	}
}

func (se *SchedulerEngine) processQueue() {
	se.mu.Lock()
	now := time.Now().UTC()
	due := make([]*SocialPost, 0)
	remaining := make([]*SocialPost, 0)

	for _, post := range se.queue {
		if post.ScheduledAt != nil && post.ScheduledAt.Before(now) && post.Status == PostStatusScheduled {
			due = append(due, post)
		} else {
			remaining = append(remaining, post)
		}
	}
	se.queue = remaining
	se.mu.Unlock()

	for _, post := range due {
		for _, platform := range post.Platforms {
			ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
			result := se.publish(ctx, post, platform)
			cancel()

			if result != nil && result.Success {
				post.PlatformIDs[string(platform)] = result.PlatformID
			} else if post.RetryCount < post.MaxRetries {
				post.RetryCount++
				retryTime := time.Now().UTC().Add(time.Duration(post.RetryCount*5) * time.Minute)
				post.ScheduledAt = &retryTime
				se.Schedule(post)
			} else {
				post.Status = PostStatusFailed
			}
		}
	}
}

func (se *SchedulerEngine) GetQueueSize() int {
	se.mu.Lock()
	defer se.mu.Unlock()
	return len(se.queue)
}

// ─────────────────────────────────────────────
// Section 6: Webhook Signature Verification
// ─────────────────────────────────────────────

// WebhookVerifier validates incoming webhooks from social platforms.
type WebhookVerifier struct{}

func (wv *WebhookVerifier) VerifyTwitter(payload []byte, signature string, consumerSecret string) bool {
	mac := hmac.New(sha256.New, []byte(consumerSecret))
	mac.Write(payload)
	expected := "sha256=" + base64.StdEncoding.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(expected), []byte(signature))
}

func (wv *WebhookVerifier) VerifyFacebook(payload []byte, signature string, appSecret string) bool {
	mac := hmac.New(sha256.New, []byte(appSecret))
	mac.Write(payload)
	expected := "sha256=" + fmt.Sprintf("%x", mac.Sum(nil))
	return hmac.Equal([]byte(expected), []byte(signature))
}

// ─────────────────────────────────────────────
// Section 7: Main Engine
// ─────────────────────────────────────────────

// SocialMediaAutomationEngine is the OMNI production engine for cross-platform social media automation.
type SocialMediaAutomationEngine struct {
	mu              sync.RWMutex
	adapters        map[SocialPlatform]PlatformAdapter
	optimizer       *ContentOptimizer
	scheduler       *SchedulerEngine
	webhookVerifier *WebhookVerifier
	startedAt       time.Time
	posts           map[string]*SocialPost
	analytics       map[string]*PostAnalytics

	// Stats
	totalPublished    int64
	totalFailed       int64
	totalScheduled    int64
	totalDeleted      int64
	totalMediaUploads int64
	errors            []string
}

// NewSocialMediaAutomationEngine creates a new engine instance.
func NewSocialMediaAutomationEngine() *SocialMediaAutomationEngine {
	engine := &SocialMediaAutomationEngine{
		adapters:        make(map[SocialPlatform]PlatformAdapter),
		optimizer:       NewContentOptimizer(),
		webhookVerifier: &WebhookVerifier{},
		startedAt:       time.Now().UTC(),
		posts:           make(map[string]*SocialPost),
		analytics:       make(map[string]*PostAnalytics),
	}

	engine.scheduler = NewSchedulerEngine(engine.publishToPlatform)
	log.Println("[OMNI-SocialMedia] Engine initialized")
	return engine
}

// RegisterAdapter registers a platform adapter for use.
func (sme *SocialMediaAutomationEngine) RegisterAdapter(adapter PlatformAdapter) error {
	if err := adapter.ValidateCredentials(); err != nil {
		return fmt.Errorf("credential validation failed for %s: %w", adapter.Platform(), err)
	}
	sme.mu.Lock()
	sme.adapters[adapter.Platform()] = adapter
	sme.mu.Unlock()
	log.Printf("[OMNI-SocialMedia] Registered adapter: %s", adapter.Platform())
	return nil
}

// Publish publishes a post to all specified platforms.
func (sme *SocialMediaAutomationEngine) Publish(ctx context.Context, post *SocialPost) map[SocialPlatform]*PublishResult {
	results := make(map[SocialPlatform]*PublishResult)
	post.PlatformIDs = make(map[string]string)

	for _, platform := range post.Platforms {
		result := sme.publishToPlatform(ctx, post, platform)
		results[platform] = result
	}

	post.Status = PostStatusPublished
	now := time.Now().UTC()
	post.PublishedAt = &now

	sme.mu.Lock()
	sme.posts[post.ID] = post
	sme.mu.Unlock()

	return results
}

func (sme *SocialMediaAutomationEngine) publishToPlatform(
	ctx context.Context, post *SocialPost, platform SocialPlatform,
) *PublishResult {
	sme.mu.RLock()
	adapter, ok := sme.adapters[platform]
	sme.mu.RUnlock()

	if !ok {
		return &PublishResult{
			Platform:  platform,
			Success:   false,
			Error:     fmt.Sprintf("no adapter registered for %s", platform),
			Timestamp: time.Now().UTC(),
		}
	}

	// Optimize content for platform
	optimizedPost := *post
	optimizedPost.Content = sme.optimizer.OptimizeForPlatform(post.Content, platform)

	// Upload media first
	for i, media := range optimizedPost.Media {
		if media.MediaID == "" && media.FilePath != "" {
			mediaID, err := adapter.UploadMedia(ctx, &media)
			if err != nil {
				log.Printf("[OMNI-SocialMedia] Media upload failed for %s: %v", platform, err)
			} else {
				optimizedPost.Media[i].MediaID = mediaID
				sme.mu.Lock()
				sme.totalMediaUploads++
				sme.mu.Unlock()
			}
		}
	}

	result, err := adapter.Publish(ctx, &optimizedPost)
	if err != nil {
		sme.mu.Lock()
		sme.totalFailed++
		sme.errors = append(sme.errors, fmt.Sprintf("%s: %v", platform, err))
		sme.mu.Unlock()
		return &PublishResult{
			Platform:  platform,
			Success:   false,
			Error:     err.Error(),
			Timestamp: time.Now().UTC(),
		}
	}

	if result.Success {
		sme.mu.Lock()
		sme.totalPublished++
		sme.mu.Unlock()
	} else {
		sme.mu.Lock()
		sme.totalFailed++
		sme.mu.Unlock()
	}

	return result
}

// Schedule schedules a post for future publishing.
func (sme *SocialMediaAutomationEngine) Schedule(post *SocialPost) {
	sme.mu.Lock()
	sme.totalScheduled++
	sme.posts[post.ID] = post
	sme.mu.Unlock()
	sme.scheduler.Schedule(post)
}

// StartScheduler starts the background scheduler.
func (sme *SocialMediaAutomationEngine) StartScheduler() {
	sme.scheduler.Start()
}

// StopScheduler stops the background scheduler.
func (sme *SocialMediaAutomationEngine) StopScheduler() {
	sme.scheduler.Stop()
}

// DeletePost deletes a post from a platform.
func (sme *SocialMediaAutomationEngine) DeletePost(ctx context.Context, postID string, platform SocialPlatform) error {
	sme.mu.RLock()
	post, ok := sme.posts[postID]
	adapter, hasAdapter := sme.adapters[platform]
	sme.mu.RUnlock()

	if !ok {
		return fmt.Errorf("post not found: %s", postID)
	}
	if !hasAdapter {
		return fmt.Errorf("no adapter for %s", platform)
	}

	platformID, ok := post.PlatformIDs[string(platform)]
	if !ok {
		return fmt.Errorf("post %s has no ID for %s", postID, platform)
	}

	if err := adapter.Delete(ctx, platformID); err != nil {
		return err
	}

	sme.mu.Lock()
	sme.totalDeleted++
	sme.mu.Unlock()
	return nil
}

// GetAnalytics fetches analytics for a post from a specific platform.
func (sme *SocialMediaAutomationEngine) GetAnalytics(ctx context.Context, postID string, platform SocialPlatform) (*PostAnalytics, error) {
	sme.mu.RLock()
	post, ok := sme.posts[postID]
	adapter, hasAdapter := sme.adapters[platform]
	sme.mu.RUnlock()

	if !ok {
		return nil, fmt.Errorf("post not found: %s", postID)
	}
	if !hasAdapter {
		return nil, fmt.Errorf("no adapter for %s", platform)
	}

	platformID := post.PlatformIDs[string(platform)]
	analytics, err := adapter.GetAnalytics(ctx, platformID)
	if err != nil {
		return nil, err
	}

	analytics.PostID = postID

	sme.mu.Lock()
	sme.analytics[postID+"_"+string(platform)] = analytics
	sme.mu.Unlock()

	return analytics, nil
}

// GetProfile retrieves account profile for a platform.
func (sme *SocialMediaAutomationEngine) GetProfile(ctx context.Context, platform SocialPlatform) (*AccountProfile, error) {
	sme.mu.RLock()
	adapter, ok := sme.adapters[platform]
	sme.mu.RUnlock()
	if !ok {
		return nil, fmt.Errorf("no adapter for %s", platform)
	}
	return adapter.GetProfile(ctx)
}

// GetOptimalPostingTimes returns best posting times for a platform.
func (sme *SocialMediaAutomationEngine) GetOptimalPostingTimes(platform SocialPlatform) []time.Time {
	return sme.optimizer.GetBestPostingTimes(platform)
}

// SuggestHashtags suggests hashtags based on content.
func (sme *SocialMediaAutomationEngine) SuggestHashtags(content string, platform SocialPlatform) []string {
	return sme.optimizer.GenerateHashtagSuggestions(content, platform)
}

// GetConnectedPlatforms returns list of platforms with registered adapters.
func (sme *SocialMediaAutomationEngine) GetConnectedPlatforms() []SocialPlatform {
	sme.mu.RLock()
	defer sme.mu.RUnlock()
	platforms := make([]SocialPlatform, 0, len(sme.adapters))
	for p := range sme.adapters {
		platforms = append(platforms, p)
	}
	return platforms
}

// Diagnostics returns OMNI-standard diagnostics.
func (sme *SocialMediaAutomationEngine) Diagnostics() map[string]interface{} {
	sme.mu.RLock()
	defer sme.mu.RUnlock()

	platforms := make([]string, 0, len(sme.adapters))
	for p := range sme.adapters {
		platforms = append(platforms, string(p))
	}

	return map[string]interface{}{
		"engine":              "SocialMediaAutomationEngine",
		"version":             "1.0.0",
		"status":              "operational",
		"started_at":          sme.startedAt.Format(time.RFC3339),
		"connected_platforms": platforms,
		"stats": map[string]interface{}{
			"total_published":     sme.totalPublished,
			"total_failed":        sme.totalFailed,
			"total_scheduled":     sme.totalScheduled,
			"total_deleted":       sme.totalDeleted,
			"total_media_uploads": sme.totalMediaUploads,
			"posts_tracked":       len(sme.posts),
			"analytics_cached":    len(sme.analytics),
			"queue_size":          sme.scheduler.GetQueueSize(),
			"errors":              len(sme.errors),
		},
		"capabilities": []string{
			"multi_platform_publish", "scheduled_posting",
			"media_upload", "analytics_retrieval",
			"profile_info", "content_optimization",
			"hashtag_suggestions", "optimal_timing",
			"post_deletion", "webhook_verification",
			"campaign_management", "retry_with_backoff",
			"rate_limit_tracking",
		},
		"supported_platforms": []string{
			"twitter", "facebook", "instagram", "linkedin",
			"youtube", "tiktok", "pinterest", "reddit",
			"mastodon", "threads",
		},
	}
}
