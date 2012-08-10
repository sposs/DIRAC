# $HeadURL$
""" GGUSTicketsClient class is a client for the GGUS Tickets DB.
"""
from suds        import WebFault
from suds.client import Client

from DIRAC import S_OK, S_ERROR

__RCSID__ = "$Id$"

class GGUSTicketsClient:
  # FIXME: Why is this a class and not just few methods?

  def __init__( self ):
    
    # create client instance using GGUS wsdl:
    self.gclient          = Client( "https://prod-ars.ggus.eu/arsys/WSDL/public/prod-ars/GGUS" )
    authInfo = self.gclient.factory.create( "AuthenticationInfo" )
    authInfo.userName     = "ticketinfo"
    authInfo.password     = "TicketInfo"
    self.gclient.set_options( soapheaders = authInfo )

################################################################################

  def getTicketsList( self, siteName, startDate = None, endDate = None ):
    """ Return tickets of entity in name
       @param name: should be the name of the site
       @param startDate: starting date (optional)
       @param endDate: end date (optional)
    """

    # prepare the query string:
    query = '\'GHD_Affected Site\'=\"' + siteName + '\" AND \'GHD_Affected VO\'="lhcb"'
    
    
    if startDate is not None:
      query = query + ' AND \'GHD_Date Of Creation\'>' + str( startDate )
    
    if endDate is not None:
      query = query + ' AND \'GHD_Date Of Creation\'<' + str( endDate )

    # create the URL to get tickets relative to the site ( opened only ! ): 
    ggusURL = 'https://ggus.eu/ws/ticket_search.php?show_columns_check[]=REQUEST_ID&\
               show_columns_check[]=TICKET_TYPE&show_columns_check[]=AFFECTED_VO&show_columns_check[]=\
               AFFECTED_SITE&show_columns_check[]=PRIORITY&show_columns_check[]=RESPONSIBLE_UNIT&show_\
               columns_check[]=STATUS&show_columns_check[]=DATE_OF_CREATION&show_columns_check[]=LAST_UPDATE&\
               show_columns_check[]=TYPE_OF_PROBLEM&show_columns_check[]=SUBJECT&ticket=&supportunit=all&su_\
               hierarchy=all&vo=lhcb&user=&keyword=&involvedsupporter=&assignto=&affectedsite=%s\
               &specattrib=0&status=open&priority=all&typeofproblem=all&ticketcategory=&mouarea=&technology_\
               provider=&date_type=creation+date&radiotf=1&timeframe=any&untouched_date=&orderticketsby=GHD_\
               INT_REQUEST_ID&orderhow=descending' % siteName
    
    # the query must be into a try block. Empty queries, though formally correct, raise an exception
    try:
      ticketList = self.gclient.service.TicketGetList( query )
    except WebFault, e:
      return S_ERROR( e )
    
    stats = self.globalStatistics( ticketList )
    if not stats[ 'OK' ]:
      return stats
    statusCount, shortDescription = stats[ 'Value' ]
    
    return S_OK( ( statusCount, ggusURL, shortDescription ) )

################################################################################
  
  @staticmethod
  def globalStatistics( ticketList ):
    '''
      Get some statistics about the tickets for the site: total number
      of tickets and number of ticket in different status
    '''
    
    selectedTickets = {} # initialize the dictionary of tickets to return
    for ticket in ticketList:
      
      _id               = ticket.GHD_Request_ID
      _status           = ticket.GHD_Status
      _shortDescription = ticket.GHD_Short_Description
      
      selectedTickets[ _id ] = {
                                'status'           : _status,
                                'shortDescription' : _shortDescription,                               
                                }      
        
    # group tickets in only 2 categories: open and terminal states
    # create a dictionary to store the short description only for tickets in open states:
    openStates     = [ 'assigned', 'in progress', 'new', 'on hold', 'reopened', 'waiting for reply' ]
    terminalStates = [ 'solved', 'unsolved', 'verified', 'closed' ]
    
    statusCount = { 'open' : 0, 'terminal' : 0 }
    
    shortDescription = {}
    
    for ticketID, ticketValues in selectedTickets.items():
      
      status = ticketValues[ 'status' ]
      
      if status in terminalStates:
        statusCount[ 'terminal' ] += 1
      elif status in openStates:
        statusCount[ 'open' ] += 1
      
        if ticketID not in shortDescription.keys():
          shortDescription[ ticketID ] = ticketValues[ 'shortDescription' ]

      else:
        return S_ERROR( '%s is not a known GGUS status' % status )  
         
    return S_OK( ( statusCount, shortDescription ) ) 

################################################################################
#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF