""" Written By Benjamin Jack Cullen

Name: http response code info / httprci
Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
Bing AI assisted dictionary creation.

"""

httprci = {
    100: {"type": "Information Response",
          "des0": "Continue",
          "des1": "This interim response indicates that the client should continue the request or ignore the response"
                  "if the request is already finished."},

    101: {"type": "Information Response",
          "des0": "Switching Protocols",
          "des1": "This code is sent in response to an Upgrade request header from the client and indicates the"
                  "protocol the server is switching to."},

    102: {"type": "Information Response",
          "des0": "Processing",
          "des1": "This code indicates that the server has received and is processing the request, but no response"
                  "is available yet."},

    103: {"type": "Information Response",
          "des0": "Early Hints",
          "des1": "This status code is primarily intended to be used with the Link header, letting the user agent"
                  "start preloading resources while the server prepares a response or pre-connect to an origin from"
                  "which the page will need resources."},

    200: {"type": "Successful Response",
          "des0": "OK",
          "des1": "The request succeeded. The result meaning of 'success' depends on the HTTP method:"
                  "GET: The resource has been fetched and transmitted in the message body."
                  "HEAD: The representation headers are included in the response without any message body."
                  "PUT or POST: The resource describing the result of the action is transmitted in the message body."
                  "TRACE: The message body contains the request message as received by the server."},

    201: {"type": "Successful Response",
          "des0": "Created",
          "des1": "The request succeeded, and a new resource was created as a result. This is typically the response"
                  "sent after POST requests, or some PUT requests."},

    202: {"type": "Successful Response",
          "des0": "Accepted",
          "des1": "The request has been received but not yet acted upon. It is noncommittal, since there is no way in"
                  "HTTP to later send an asynchronous response indicating the outcome of the request. It is intended"
                  "for cases where another process or server handles the request, or for batch processing."},

    203: {"type": "Successful Response",
          "des0": "Non-Authoritative Information",
          "des1": "This response code means the returned metadata is not exactly the same as is available from the"
                  "origin server, but is collected from a local or a third-party copy. This is mostly used for mirrors"
                  "or backups of another resource. Except for that specific case, the 200 OK response is preferred to"
                  "this status."},

    204: {"type": "Successful Response",
          "des0": "No Content",
          "des1": "There is no content to send for this request, but the headers may be useful. The user agent may"
                  "update its cached headers for this resource with the new ones."},

    205: {"type": "Successful Response",
          "des0": "Reset Content",
          "des1": "Tells the user agent to reset the document which sent this request."},

    206: {"type": "Successful Response",
          "des0": "Partial Content",
          "des1": "This response code is used when the Range header is sent from the client to request only part of a"
                  "resource."},

    207: {"type": "Successful Response",
          "des0": "Multi-Status",
          "des1": "Conveys information about multiple resources, for situations where multiple status codes might be"
                  "appropriate."},

    208: {"type": "Successful Response",
          "des0": "Already Reported (WebDAV)",
          "des1": "Used inside a <dav:propstat> response element to avoid repeatedly enumerating the internal members"
                  "of multiple bindings to the same collection."},

    226: {"type": "Successful Response",
          "des0": "IM Used (HTTP Delta encoding)",
          "des1": "The server has fulfilled a GET request for the resource, and the response is a representation of"
                  "the result of one or more instance-manipulations applied to the current instance."},

    300: {"type": "Redirection Message",
          "des0": "Multiple Choices",
          "des1": "The request has more than one possible response. The user agent or user should choose one of them."
                  "(There is no standardized way of choosing one of the responses, but HTML links to the possibilities"
                  "are recommended so the user can pick.)"},

    301: {"type": "Redirection Message",
          "des0": "Moved Permanently",
          "des1": "The URL of the requested resource has been changed permanently. The new URL is given in the"
                  "response."},

    302: {"type": "Redirection Message",
          "des0": "Found",
          "des1": "This response code means that the URI of requested resource has been changed temporarily. Further"
                  "changes in the URI might be made in the future. Therefore, this same URI should be used by the"
                  "client in future requests."},

    303: {"type": "Redirection Message",
          "des0": "See Other",
          "des1": "The server sent this response to direct the client to get the requested resource at another URI"
                  "with a GET request."},

    304: {"type": "Redirection Message",
          "des0": "Not Modified",
          "des1": "This is used for caching purposes. It tells the client that the response has not been modified, so"
                  "the client can continue to use the same cached version of the response."},

    305: {"type": "Redirection Message",
          "des0": "Use Proxy",
          "des1": "Defined in a previous version of the HTTP specification to indicate that a requested response must"
                  "be accessed by a proxy. It has been deprecated due to security concerns regarding in-band"
                  "configuration of a proxy."},

    306: {"type": "Redirection Message",
          "des0": "unused",
          "des1": "This response code is no longer used; it is just reserved. It was used in a previous version of the"
                  "HTTP/1.1 specification."},

    307: {"type": "Redirection Message",
          "des0": "Temporary Redirect",
          "des1": "The server sends this response to direct the client to get the requested resource at another URI"
                  "with the same method that was used in the prior request. This has the same semantics as the 302"
                  "Found HTTP response code, with the exception that the user agent must not change the HTTP method"
                  "used: if a POST was used in the first request, a POST must be used in the second request."},

    308: {"type": "Redirection Message",
          "des0": "Permanent Redirect",
          "des1": "This means that the resource is now permanently located at another URI, specified by the Location:"
                  "HTTP Response header. This has the same semantics as the 301 Moved Permanently HTTP response code,"
                  "with the exception that the user agent must not change the HTTP method used: if a POST was used in"
                  "the first request, a POST must be used in the second request."},

    400: {"type": "Client Error Response",
          "des0": "Bad Request",
          "des1": "The server cannot or will not process the request due to something that is perceived to be a client"
                  "error (e.g., malformed request syntax, invalid request message framing, or deceptive request"
                  "routing)."},

    401: {"type": "Client Error Response",
          "des0": "Unauthorized",
          "des1": "Although the HTTP standard specifies 'unauthorized', semantically this response means"
                  "'unauthenticated'. That is, the client must authenticate itself to get the requested response."},

    402: {"type": "Client Error Response",
          "des0": "Payment Required",
          "des1": "This response code is reserved for future use. The initial aim for creating this code was using it"
                  "for digital payment systems, however this status code is used very rarely and no standard"
                  "convention exists."},

    403: {"type": "Client Error Response",
          "des0": "Forbidden",
          "des1": "The client does not have access rights to the content; that is, it is unauthorized, so the server"
                  "is refusing to give the requested resource. Unlike 401 Unauthorized, the client's identity is known"
                  "to the server."},

    404: {"type": "Client Error Response",
          "des0": "Not Found",
          "des1": "The server cannot find the requested resource. In the browser, this means the URL is not"
                  "recognized. In an API, this can also mean that the endpoint is valid but the resource itself does"
                  "not exist. Servers may also send this response instead of 403 Forbidden to hide the existence of a"
                  "resource from an unauthorized client. This response code is probably the most well known due to its"
                  "frequent occurrence on the web."},

    405: {"type": "Client Error Response",
          "des0": "Method Not Allowed",
          "des1": "The request method is known by the server but is not supported by the target resource. For example,"
                  "an API may not allow calling DELETE to remove a resource."},

    406: {"type": "Client Error Response",
          "des0": "Not Acceptable",
          "des1": "This response is sent when the web server, after performing server-driven content negotiation,"
                  "doesn't find any content that conforms to the criteria given by the user agent."},

    407: {"type": "Client Error Response",
          "des0": "Proxy Authentication Required",
          "des1": "This is similar to 401 Unauthorized but authentication is needed to be done by a proxy."},

    408: {"type": "Client Error Response",
          "des0": "Request Timeout",
          "des1": "This response is sent on an idle connection by some servers, even without any previous request by"
                  "the client. It means that the server would like to shut down this unused connection. This response"
                  "is used much more since some browsers, like Chrome, Firefox 27+, or IE9, use HTTP pre-connection"
                  "mechanisms to speed up surfing. Also note that some servers merely shut down the connection without"
                  "sending this message."},

    409: {"type": "Client Error Response",
          "des0": "Conflict",
          "des1": "This response is sent when a request conflicts with the current state of the server."},

    410: {"type": "Client Error Response",
          "des0": "Gone",
          "des1": "This response is sent when the requested content has been permanently deleted from server, with no"
                  "forwarding address. Clients are expected to remove their caches and links to the resource. The HTTP"
                  "specification intends this status code to be used for 'limited-time, promotional services'. APIs"
                  "should not feel compelled to indicate resources that have been deleted with this status code."},

    411: {"type": "Client Error Response",
          "des0": "Length Required",
          "des1": "Server rejected the request because the Content-Length header field is not defined and the server"
                  "requires it."},

    412: {"type": "Client Error Response",
          "des0": "Precondition Failed",
          "des1": "The client has indicated preconditions in its headers which the server does not meet."},

    413: {"type": "Client Error Response",
          "des0": "Payload Too Large",
          "des1": "Request entity is larger than limits defined by server. The server might close the connection or"
                  "return an Retry-After header field."},

    414: {"type": "Client Error Response",
          "des0": "URI Too Long",
          "des1": "The URI requested by the client is longer than the server is willing to interpret."},

    415: {"type": "Client Error Response",
          "des0": "Unsupported Media Type",
          "des1": "The media format of the requested data is not supported by the server, so the server is rejecting"
                  "the request."},

    416: {"type": "Client Error Response",
          "des0": "Range Not Satisfiable",
          "des1": "The range specified by the Range header field in the request cannot be fulfilled. It's possible"
                  "that the range is outside the size of the target URI's data."},

    417: {"type": "Client Error Response",
          "des0": "Expectation Failed",
          "des1": "This response code means the expectation indicated by the Expect request header field cannot be met"
                  "by the server."},

    418: {"type": "Client Error Response",
          "des0": "I'm a teapot",
          "des1": "The server refuses the attempt to brew coffee with a teapot."},

    421: {"type": "Client Error Response",
          "des0": "Misdirected Request",
          "des1": "The request was directed at a server that is not able to produce a response. This can be sent by a"
                  "server that is not configured to produce responses for the combination of scheme and authority that"
                  "are included in the request URI."},

    422: {"type": "Client Error Response",
          "des0": "Unprocessable Entity",
          "des1": "The request was well-formed but was unable to be followed due to semantic errors."},

    423: {"type": "Client Error Response",
          "des0": "Locked",
          "des1": "The resource that is being accessed is locked."},

    424: {"type": "Client Error Response",
          "des0": "Failed Dependency",
          "des1": "The request failed due to failure of a previous request."},

    425: {"type": "Client Error Response",
          "des0": "Too Early",
          "des1": "Indicates that the server is unwilling to risk processing a request that might be replayed."},

    426: {"type": "Client Error Response",
          "des0": "Upgrade Required",
          "des1": "The server refuses to perform the request using the current protocol but might be willing to do so"
                  "after the client upgrades to a different protocol. The server sends an Upgrade header in a 426"
                  "response to indicate the required protocol(s)."},

    428: {"type": "Client Error Response",
          "des0": "Precondition Required",
          "des1": "The origin server requires the request to be conditional. This response is intended to prevent the"
                  "'lost update' problem, where a client GETs a resource's state, modifies it and PUTs it back to the"
                  "server, when meanwhile a third party has modified the state on the server, leading to a conflict."},

    429: {"type": "Client Error Response",
          "des0": "Too Many Requests",
          "des1": "The user has sent too many requests in a given amount of time ('rate limiting')."},

    431: {"type": "Client Error Response",
          "des0": "Request Header Fields Too Large",
          "des1": "The server is unwilling to process the request because its header fields are too large. The request"
                  "may be resubmitted after reducing the size of the request header fields."},

    451: {"type": "Client Error Response",
          "des0": "Unavailable For Legal Reasons",
          "des1": "The user agent requested a resource that cannot legally be provided, such as a web page censored by"
                  "a government."},

    500: {"type": "Server Error Response",
          "des0": "Internal Server Error",
          "des1": "The server has encountered a situation it does not know how to handle."},

    501: {"type": "Server Error Response",
          "des0": "Not Implemented",
          "des1": "The request method is not supported by the server and cannot be handled. The only methods that"
                  "servers are required to support (and therefore that must not return this code) are GET and HEAD."},

    502: {"type": "Server Error Response",
          "des0": "Bad Gateway",
          "des1": "This Error response means that the server, while working as a gateway to get a response needed to"
                  "handle the request, got an invalid response."},

    503: {"type": "Server Error Response",
          "des0": "Service Unavailable",
          "des1": "The server is not ready to handle the request. Common causes are a server that is down for"
                  "maintenance or that is overloaded. Note that together with this response, a user-friendly page"
                  "explaining the problem should be sent. This response should be used for temporary conditions and"
                  "the Retry-After HTTP header should, if possible, contain the estimated time before the recovery of"
                  "the service. The webmaster must also take care about the caching-related headers that are sent"
                  "along with this response, as these temporary condition responses should usually not be cached."},

    504: {"type": "Server Error Response",
          "des0": "Gateway Timeout",
          "des1": "This Error response is given when the server is acting as a gateway and cannot get a response in"
                  "time."},

    505: {"type": "Server Error Response",
          "des0": "HTTP Version Not Supported",
          "des1": "The HTTP version used in the request is not supported by the server."},

    506: {"type": "Server Error Response",
          "des0": "Variant Also Negotiates",
          "des1": "The server has an internal configuration error: the chosen variant resource is configured to engage"
                  "in transparent content negotiation itself, and is therefore not a proper end point in the"
                  "negotiation process."},

    507: {"type": "Server Error Response",
          "des0": "Insufficient Storage",
          "des1": "The method could not be performed on the resource because the server is unable to store the"
                  "representation needed to successfully complete the request."},

    508: {"type": "Server Error Response",
          "des0": "Loop Detected",
          "des1": "The server detected an infinite loop while processing the request."},

    510: {"type": "Server Error Response",
          "des0": "Not Extended",
          "des1": "Further extensions to the request are required for the server to fulfill it."},

    511: {"type": "Server Error Response",
          "des0": "Network Authentication Required",
          "des1": "Indicates that the client needs to authenticate to gain network access."},

    524: {"type": "Server Error Response",
          "des0": "Gateway Timeout Error",
          "des1": "The 524 gateway Timeout Error is a Cloudflare-specific HTTP status code that indicates that the"
                  "connection to the server has been closed due to a timeout."}
}


def get(code=int, display=int):
    """ Returns HTTP response code information in various types & string formats.

    code = HTTP Status Code
    display = Display mode. Select from available output type/format

    display=int(0) = Return: a list of results
    display=int(1) = Return formatted short results (multi line)
    display=int(2) = Return formatted long results (multi line)
    display=int(3) = Return formatted short results (single line)

    Example: httprci.get(200, display=int(3))

    """

    des0 = httprci.get(code).get('des0')
    des1 = httprci.get(code).get('des1')
    t = httprci.get(code).get('type')

    if display == int(0):
        return [code, t, des0, des1]

    elif display == int(1):
        return f'Response Code: {code}\n{t}\n{des0}'

    elif display == int(2):
        return f'Response Code: {code}\n{t}\n{des0}\n{des1}'

    elif display == int(3):
        return f'{code} : {t} : {des0}'

