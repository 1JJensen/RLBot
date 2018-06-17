﻿using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace RLBotDotNet.Server
{
    /// <summary>
    /// A class used for running a server to get bot data from Python clients.
    /// E.g. Will receive "{ name = "Bot1", team = 1, index = 3 }"
    /// </summary>
    public class BotManagerServer
    {
        private TcpListener listener;
        public event EventHandler BotReceived;

        /// <summary>
        /// Event that gets raised whenever a message is received from the Python client.
        /// </summary>
        protected virtual void OnBotReceived(BotReceivedEventArgs e)
        {
            BotReceived?.Invoke(this, e);
        }

        /// <summary>
        /// Starts the server, which continously listens for clients until it is stopped.
        /// </summary>
        /// <param name="port">The port to run the server on.</param>
        public void Start(int port)
        {
            if (listener == null)
            {
                listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
                listener.Start();

                while (true)
                {
                    TcpClient client = listener.AcceptTcpClient();
                    NetworkStream stream = client.GetStream();
                    byte[] buffer = new byte[client.ReceiveBufferSize];
                    int bytes = stream.Read(buffer, 0, client.ReceiveBufferSize);

                    string receivedString = Encoding.ASCII.GetString(buffer, 0, bytes);
                    OnBotReceived(new BotReceivedEventArgs(receivedString));

                    // TODO: Do some verification to know that the data was sent correctly.
                    // E.g. Echo check

                    client.Close();
                }
            }
        }

        /// <summary>
        /// Stops the server if it is running.
        /// </summary>
        public void Stop()
        {
            if (listener != null)
            {
                listener.Stop();
                listener = null;
            }
        }
    }
}
