#include <pebble.h>

static Window *s_window;	
	
// Keys for AppMessage Dictionary
// These should correspond to the values you defined in appinfo.json/Settings
//enum {
//	MESSAGE_KEY_STEP = 0,	
//	MESSAGE_KEY_ACTIVE = 1,
//  MESSAGE_KEY_WALKED = 2,
//  MESSAGE_KEY_SLEEP = 3,
//  MESSAGE_KEY_REST = 4,
//  MESSAGE_KEY_HEART = 5
//};

static Layer *s_canvas_layer;

static int step_count = -1;
static int active_secs = -1;
static int walked_meters = -1;
static int sleep_secs = -1;
static int restful_secs = -1;
static int heart_rate_bpm = -1;

static void canvas_update_proc(Layer *layer, GContext *ctx) {
  // Custom drawing happens here!
  // Load the font
  GFont font = fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD);
  // Set the color
  graphics_context_set_text_color(ctx, GColorBlack);
  
  char text[128];
  snprintf(text, sizeof(text), "Buddy 1.0\nSteps: %d\nActive: %d\nWalked: %d\nSleep: %d\nRestful: %d\nBPM: %d\n",step_count,active_secs,walked_meters,sleep_secs,restful_secs,heart_rate_bpm);
  
  // Determine a reduced bounding box
  GRect layer_bounds = layer_get_bounds(layer);
  GRect bounds = GRect(layer_bounds.origin.x, layer_bounds.origin.y+20,
                      layer_bounds.size.w, layer_bounds.size.h);

  // Calculate the size of the text to be drawn, with restricted space
  GSize text_size = graphics_text_layout_get_content_size(text, font, bounds, GTextOverflowModeWordWrap, GTextAlignmentCenter);
  
  // Draw the text
  graphics_draw_text(ctx, text, font, bounds, GTextOverflowModeWordWrap, GTextAlignmentCenter, NULL);
  
  
}

// Called when a message is received from PebbleKitJS
static void in_received_handler(DictionaryIterator *received, void *context) {
	Tuple *tuple;
	
	tuple = dict_find(received, MESSAGE_KEY_REQUEST);
	if(tuple) {
		APP_LOG(APP_LOG_LEVEL_DEBUG, "Received Request: %d", (int)tuple->value->uint32); 
	}
  
  //send_message();
}

// Called when an incoming message from PebbleKitJS is dropped
static void in_dropped_handler(AppMessageResult reason, void *context) {	
  APP_LOG(APP_LOG_LEVEL_INFO, "Incoming message dropped!");
}

// Called when PebbleKitJS does not acknowledge receipt of a message
static void out_failed_handler(DictionaryIterator *failed, AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_INFO, "Did not acknowledge receipt of a message");
}

static void outbox_sent_handler(DictionaryIterator *iterator, void *context) {
  APP_LOG(APP_LOG_LEVEL_INFO, "Outbox send success!");
  vibes_short_pulse();
}

static int get_health_metric(time_t start, time_t end, HealthMetric metric)
{     
      // Check the metric has data available for today
      HealthServiceAccessibilityMask mask = health_service_metric_accessible(metric, start, end);

      if(mask & HealthServiceAccessibilityMaskAvailable) {
         // Data is available!
         return (int) health_service_sum_today(metric);
      } else {
         // No data recorded yet today
         APP_LOG(APP_LOG_LEVEL_ERROR, "Data unavailable!");
      }
      return -1;
}

static void send_awake_data(int steps, int active_secs, int walked_meters)
{
   // Declare the dictionary's iterator
   DictionaryIterator *out_iter;

   // Prepare the outbox buffer for this message
   AppMessageResult result = app_message_outbox_begin(&out_iter);
   if(result == APP_MSG_OK) 
   {
      dict_write_int(out_iter, MESSAGE_KEY_STEP, &steps, sizeof(int), true);
      dict_write_int(out_iter, MESSAGE_KEY_ACTIVE, &active_secs, sizeof(int), true);
      dict_write_int(out_iter, MESSAGE_KEY_WALKED, &walked_meters, sizeof(int), true);
      dict_write_end(out_iter);
      // Send this message
      result = app_message_outbox_send();
      if(result != APP_MSG_OK)
         APP_LOG(APP_LOG_LEVEL_ERROR, "Error sending the awake data: %d", (int)result);
   } else // The outbox cannot be used right now
      APP_LOG(APP_LOG_LEVEL_ERROR, "Error preparing the awake data: %d", (int)result);  
}

static void send_sleep_data(int sleep_secs, int restful_secs)
{
   // Declare the dictionary's iterator
   DictionaryIterator *out_iter;

   // Prepare the outbox buffer for this message
   AppMessageResult result = app_message_outbox_begin(&out_iter);
   if(result == APP_MSG_OK) 
   {
      dict_write_int(out_iter, MESSAGE_KEY_SLEEP, &sleep_secs, sizeof(int), true);
      dict_write_int(out_iter, MESSAGE_KEY_REST, &restful_secs, sizeof(int), true);
      dict_write_end(out_iter);

      // Send this message
      result = app_message_outbox_send();
      if(result != APP_MSG_OK)
         APP_LOG(APP_LOG_LEVEL_ERROR, "Error sending the sleep data: %d", (int)result);
   } else // The outbox cannot be used right now
      APP_LOG(APP_LOG_LEVEL_ERROR, "Error preparing the sleep data: %d", (int)result);  
}

static void send_heart_data(int heart)
{
   // Declare the dictionary's iterator
   DictionaryIterator *out_iter;

   // Prepare the outbox buffer for this message
   AppMessageResult result = app_message_outbox_begin(&out_iter);
   if(result == APP_MSG_OK) 
   {
      dict_write_int(out_iter, MESSAGE_KEY_HEART, &heart, sizeof(int), true);
      dict_write_end(out_iter);
      // Send this message
      result = app_message_outbox_send();
      if(result != APP_MSG_OK)
         APP_LOG(APP_LOG_LEVEL_ERROR, "Error sending the heart data: %d", (int)result);
   } else // The outbox cannot be used right now
      APP_LOG(APP_LOG_LEVEL_ERROR, "Error preparing the heart data: %d", (int)result);  
}

static void health_handler(HealthEventType event, void *context) {
  time_t start = time_start_of_today();
  time_t end = time(NULL);
  // Which type of event occurred?
  switch(event) {
    case HealthEventSignificantUpdate:
      APP_LOG(APP_LOG_LEVEL_INFO, "New HealthService HealthEventSignificantUpdate event");
      step_count = get_health_metric(start, end, HealthMetricStepCount);
      active_secs = get_health_metric(start, end, HealthMetricActiveSeconds);
      walked_meters = get_health_metric(start, end, HealthMetricWalkedDistanceMeters);
      if (step_count > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Steps today: %d", step_count);
      if (active_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Active seconds today: %d", active_secs);
      if (walked_meters > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Meters walked today: %d", walked_meters);
      //send_awake_data(step_count, active_secs, walked_meters);
    
      sleep_secs = get_health_metric(start, end, HealthMetricSleepSeconds);
      restful_secs = get_health_metric(start, end, HealthMetricSleepRestfulSeconds);
      if (sleep_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Seconds asleep today: %d", sleep_secs);
      if (restful_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Restful sleep seconds today: %d", restful_secs);
      //send_sleep_data(sleep_secs, restful_secs);
    break;
    
    case HealthEventMovementUpdate:
      APP_LOG(APP_LOG_LEVEL_INFO, "New HealthService HealthEventMovementUpdate event");
      step_count = get_health_metric(start, end, HealthMetricStepCount);
      active_secs = get_health_metric(start, end, HealthMetricActiveSeconds);
      walked_meters = get_health_metric(start, end, HealthMetricWalkedDistanceMeters);
      if (step_count > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Steps today: %d", step_count);
      if (active_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Active seconds today: %d", active_secs);
      if (walked_meters > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Meters walked today: %d", walked_meters);
      send_awake_data(step_count, active_secs, walked_meters);
      layer_mark_dirty(s_canvas_layer);
    break;
    
    case HealthEventSleepUpdate:
      APP_LOG(APP_LOG_LEVEL_INFO, "New HealthService HealthEventSleepUpdate event");
      sleep_secs = get_health_metric(start, end, HealthMetricSleepSeconds);
      restful_secs = get_health_metric(start, end, HealthMetricSleepRestfulSeconds);
      if (sleep_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Seconds asleep today: %d", sleep_secs);
      if (restful_secs > -1) 
         APP_LOG(APP_LOG_LEVEL_INFO, "Restful sleep seconds today: %d", restful_secs);
      send_sleep_data(sleep_secs, restful_secs);
      layer_mark_dirty(s_canvas_layer);
    break;
    
    case HealthEventHeartRateUpdate:
      APP_LOG(APP_LOG_LEVEL_INFO, "New HealthService HealthEventHeartRateUpdate event");
      heart_rate_bpm = health_service_peek_current_value(HealthMetricHeartRateBPM);
      if (heart_rate_bpm > -1) 
      {
         APP_LOG(APP_LOG_LEVEL_INFO, "Current heart Rate BPM: %d", heart_rate_bpm);
         send_heart_data(heart_rate_bpm);
         layer_mark_dirty(s_canvas_layer);
      }
    break;
    
    case HealthEventMetricAlert:
      APP_LOG(APP_LOG_LEVEL_INFO,
              "New HealthService HealthEventMetricAlert event");
      break;
  }
}

static void init(void) {
	s_window = window_create();
	window_stack_push(s_window, true);
  
  GRect bounds = layer_get_bounds(window_get_root_layer(s_window));
  // Create canvas layer
  s_canvas_layer = layer_create(bounds);
  
  // Assign the custom drawing procedure
  layer_set_update_proc(s_canvas_layer, canvas_update_proc);

  // Add to Window
  layer_add_child(window_get_root_layer(s_window), s_canvas_layer);
	
	// Register AppMessage handlers
	app_message_register_inbox_received(in_received_handler); 
	app_message_register_inbox_dropped(in_dropped_handler); 
	app_message_register_outbox_failed(out_failed_handler);
  app_message_register_outbox_sent(outbox_sent_handler);

  // Initialize AppMessage inbox and outbox buffers with a suitable size
  const int inbox_size = 128;
  const int outbox_size = 128;
	app_message_open(inbox_size, outbox_size);
  
  #if defined(PBL_HEALTH)
// Attempt to subscribe 
if(!health_service_events_subscribe(health_handler, NULL)) {
  APP_LOG(APP_LOG_LEVEL_ERROR, "Health not available!");
}
#else
APP_LOG(APP_LOG_LEVEL_ERROR, "Health not available!");
#endif
}

static void deinit(void) {
	app_message_deregister_callbacks();
	window_destroy(s_window);
}

int main( void ) {
	init();
	app_event_loop();
	deinit();
}
