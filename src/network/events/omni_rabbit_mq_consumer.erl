-module(omni_rabbit_mq_consumer).
-behaviour(gen_server).

-include_lib("amqp_client/include/amqp_client.hrl").

%% API
-export([start_link/0]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {connection, channel}).

%% OMNI Event Layer: RabbitMQ AMQP Consumer for Distributed Logging

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

init([]) ->
    %% Connect to local/remote RabbitMQ cluster
    {ok, Connection} = amqp_connection:start(#amqp_params_network{host = "localhost"}),
    {ok, Channel} = amqp_connection:open_channel(Connection),

    %% Declare the OMNI exchange and queue
    Exchange = <<"omni_events_exchange">>,
    Queue = <<"omni_log_queue">>,
    
    amqp_channel:call(Channel, #'exchange.declare'{exchange = Exchange, type = <<"direct">>}),
    #'queue.declare_ok'{} = amqp_channel:call(Channel, #'queue.declare'{queue = Queue}),
    amqp_channel:call(Channel, #'queue.bind'{queue = Queue, exchange = Exchange, routing_key = <<"log.error">>}),

    %% Subscribe to queue
    amqp_channel:subscribe(Channel, #'basic.consume'{queue = Queue, no_ack = false}, self()),

    {ok, #state{connection = Connection, channel = Channel}}.

handle_info(#'basic.consume_ok'{}, State) ->
    {noreply, State};

handle_info({#'basic.deliver'{delivery_tag = Tag}, #amqp_msg{payload = Payload}}, State) ->
    %% Process the structured log payload securely
    io:format("OMNI Event Received: ~p~n", [Payload]),
    
    %% Sink to durable storage or alert manager
    %% omni_telemetry_sink:write(Payload),

    %% Acknowledge message
    amqp_channel:cast(State#state.channel, #'basic.ack'{delivery_tag = Tag}),
    {noreply, State}.

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, State) ->
    amqp_channel:close(State#state.channel),
    amqp_connection:close(State#state.connection),
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
