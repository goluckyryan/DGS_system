#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string>
#include <time.h>
#include <sys/stat.h>
#include <map>
#include <vector>

const int debug = 0;
const int max_displayCount = 1;
int displayCount = 0;

#include "constant.h" // for TRIG_DATA_SIZE and TRIG_PACKET_LENGTH

// #define ENABLE_GEB_HEADER

enum ReplyType{
  INSUFF_DATA = 5,
  SERVER_SUMMARY = 4
};

enum ReplyStatus{
  Fail_to_connect = -4,
  Insufficent_data = -1,
  Acq_stopped = -2,
  No_respone = -3
};

enum DataStatus{
  Good,
  TypeD_RunIsDone,
  DIG_inComplete,
  DIG_fileOpenError,
  TRIG_inComplete,
  TRIG_fileOpenError,
  UnknownDataType
};

int netSocket = -1;

#ifdef ENABLE_GEB_HEADER
  struct gebData{
    int32_t type;										 /* type of data following */
    int32_t length;
    uint64_t timestamp;
  };
  typedef struct gebData GEBDATA;
#endif

// uint32_t data[DEFAULT_DATA_SIZE];
std::vector<uint32_t> data(DEFAULT_DATA_SIZE); // for dynamic size, default to DEFAULT_DATA_SIZE

class OutFile{
public:
  FILE * file;
  int count;
  long long fileSize;
  char outFileName[1000];
  size_t writeByte;
  size_t totalWrittenByte;
  std::string runName;

  OutFile(){
    file = NULL;
    count = 0;
    fileSize = 0;
    writeByte = 0;
    totalWrittenByte = 0;
  }
  ~OutFile(){
    CloseFile();
  }

  int NewFile(std::string extraFileName, int board_id, int ch_id){
    sprintf (outFileName, "%s_%03i_%4.4i_%01X%s", runName.c_str(), count, board_id, ch_id, extraFileName.c_str());
    file = fopen(outFileName, "ab");
    if (!file) {
      printf("\033[31m Failed to open file (%s) for writing. \033[0m\n", outFileName);
      return -1;
    }else{
      printf("\033[34m Opened %s \033[0m \n", outFileName);
      return 1;
    }
  }

  int OpenFile(std::string extraFileName, int board_id, int ch_id){
    if( file == NULL){
      return NewFile(extraFileName, board_id, ch_id);
    }else{
      if( fileSize > MAX_FILE_SIZE_BYTE){
        printf("\033[31m File size (%lld Byte) exceeds limit (%lld Byte). Closing file %s and creating new file. \033[0m\n", 
               fileSize, MAX_FILE_SIZE_BYTE, outFileName);
        CloseFile();
        count ++;
        fileSize = 0;
        return NewFile(extraFileName, board_id, ch_id);
      }
      return 1; // file is already open
    }
    return 0;
  }

  void CloseFile(){
    if ( file == NULL) return;
    fileSize = ftell(file);
    fclose(file);
    file = NULL; 
    if (chmod(outFileName, S_IRUSR | S_IRGRP | S_IROTH) == 0) {
      printf("Closed %s and set to read-only | file size : %.3f Mbytes\n", outFileName, fileSize/1024.0/1024.0);
    } else {
      printf("Closed %s but set to read-only fail.\n", outFileName);
    }
    fflush(stdout);
  }

  bool Write(const void* data, size_t size, size_t countToWrite = 1) {
    if (!file) return false;
    // printf("Writing %s | size = %zu, count = %zu | filePos : %lu (%lu)\n", outFileName, size, countToWrite, ftell(file), ftell(file)/4);
    // for( size_t i = 0; i < size/4; i++) printf("%3d     %08X \n", i, ((uint32_t*)data)[i]);
    
    uint32_t firstword = ((uint32_t*)data)[0];
    if( firstword != 0xAAAAAAAA && firstword != 0xAAAA0000 ){
      printf("\033[31m File Wirte ERROR. Data type is not DIG or TRIG. \033[0m\n");
      return false;
    }

    size_t written = fwrite(data, size, countToWrite, file);
    writeByte += written * size;    
    totalWrittenByte += written * size;
    if(written != countToWrite ) printf("write error\n.");
    fflush(file);
    // printf("\033[34m Wrote %zu bytes to %s | write btye : %zu, filePos : %lu (%lu) \033[0m\n", 
    //        written * size, outFileName, totalWrittenByte, ftell(file), ftell(file)/4);
    fileSize = ftell(file);
    return written == countToWrite;
  }

  size_t GetWrittenByte(){
    size_t haha = writeByte;
    writeByte = 0;
    return haha;
  }

  size_t GetFileSize() const{ return fileSize + MAX_FILE_SIZE_BYTE * count; }

};

// OutFile outFile[MAX_NUM_BOARD][MAX_NUM_CHANNEL]; // save each channel
// std::map<std::pair<int, int>, OutFile*> outFileMap; // map of OutFile objects indexed by (board_id, ch_id)

std::vector<OutFile*> outFileList;
std::map<int, int> outFileMap; // map  fileID to outFileList index

void SetUpConnection( std::string serverIP = "192.168.203.211", int serverPort = 9001){
  const double waitSec = 0.1;
  struct sockaddr_in server_addr;

  //============ Setup server address struct
  memset(&server_addr, 0, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(serverPort);
  if (inet_pton(AF_INET, serverIP.c_str(), &server_addr.sin_addr) <= 0) {
    printf("Invalid address/Address not supported\n");
    return;
  }

  //============ attemp to estabish connection
  int retryCount = 0;
  do{
    // Create netSocket
    netSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (netSocket < 0) {
      printf("netSocket creation failed!\n");
      return;
    }

    // Attempt to connect
    if (connect(netSocket, (struct sockaddr*)&server_addr, sizeof(server_addr)) == 0) {
      printf("Connected to server. %s\n", serverIP.c_str());
      break;
    } else {
      if( retryCount == 0 ) printf("Connection failed %s, retrying in %.2f seconds... (retry will not display)\n", serverIP.c_str(), waitSec);
      close(netSocket);
      usleep(waitSec * 1000000); // sleep for 0.1 s
      netSocket = -1;
      retryCount++;
    }
  }while(netSocket < 0 );

  // printf("netSocket = %d \n", netSocket);

}

int GetData(){ //return bytes_received.
  int replyType = 0;
  int reply[4]; // 0 = Type, 1 = Record Size in Byte, 2 = Status, 3 = num. of record

  int request = htonl(1);
  if( send(netSocket, &request, sizeof(request), 0) < 0 ){
    printf("fail to send request. \n");
    // printf("fail to send request. retry after 2 sec.\n");
    // sleep(2);
    // continue;
    return Fail_to_connect;
  }else{
    if( debug > 3 ) printf("Request sent. ");
  }
  
  int bytes_received  = recv(netSocket, ((char *) &reply), sizeof(reply), 0);
  if (bytes_received > 0) {
    if( debug > 1){
      printf("\n");
      printf("Byte received : %d \n", bytes_received);
      printf("received data = \n");
      printf("          Type : %d\n", ntohl(reply[0]) );
      printf("   Record size : %d Byte\n", ntohl(reply[1]) );
      printf("        Status : %d\n", ntohl(reply[2]) );
      printf("   Num. Record : %d\n", ntohl(reply[3]) );
    }

    replyType = ntohl(reply[0]);

    if( replyType == SERVER_SUMMARY){
      if(debug > 3 ) printf("Server summary.\n");
    }else if ( replyType == INSUFF_DATA){
      if(debug > 3 ) printf("Received Insufficient data. \n");
      return Insufficent_data;
    }else{
      printf("No data\n");
      return Acq_stopped;
    }    

    int recordByte = ntohl(reply[1]);
    int numRecord = ntohl(reply[3]);

    size_t total_bytes_received = 0;

    // if( (unsigned int)recordByte* numRecord > sizeof(data) ){
    //   printf("\033[31m ERROR. Received data (%d) is too large (> %zu). \033[0m\n", recordByte*numRecord, sizeof(data));
    //   return Insufficent_data;
    // }

    size_t required_size_bytes = recordByte * numRecord;

    if( required_size_bytes > data.size() * sizeof(uint32_t) ){
      data.resize((required_size_bytes + 3)/4); //roudn up to nearest word
      printf("\033[31mResized data to %zu words = %zu Bytes.\033[0m\n", data.size(), data.size()*4);
    }

    do{
      int bytes_received = recv(netSocket, (char*)data.data() + total_bytes_received, required_size_bytes - total_bytes_received, 0);
      int word_received = bytes_received/4;
      total_bytes_received += bytes_received;
      
      if( bytes_received <= 0 ){
        if( bytes_received < 0 ) printf("Error receiving data. \n");
        else printf("Connection closed by server.\n");
        return No_respone;
      }
 
      if( debug > 1 ) printf("Received %d bytes = %d words | total received %ld Bytes, Record size %d bytes\n", bytes_received, word_received, total_bytes_received, recordByte*numRecord);
    }while(total_bytes_received < required_size_bytes);

    if( debug > 0 ) printf("total received %ld Bytes = %ld words, Record size %d bytes\n", total_bytes_received, total_bytes_received/4, recordByte*numRecord);
    if( total_bytes_received != required_size_bytes ){
      printf("\033[1;31m !!!! ERROR. Received bytes (%ld) is not equal to expected (%d). \033[0m\n", total_bytes_received, recordByte * numRecord);
      return Insufficent_data;
    }

    // for( int i = 0; i < total_bytes_received/4; i++){
    //   printf("GetData: %3d | 0x%08X\n", i, data[i]);
    // }
    
    return total_bytes_received;

  } else {
    printf("No response or connection closed.\n");
    return No_respone;
  }
  
}

int DumpData(int bytes_received){
  if( bytes_received <= 0 ) return -1 ;

  FILE* file = fopen("output.bin", "ab");
  if (!file) {
    printf("Failed to open file (output.bin) for writing.\n");
    return 1;
  }

  size_t items_written = fwrite(data.data(), 1, bytes_received, file);
  fclose(file);

  printf("Wrote %zu bytes to output.bin | received %d bytes\n", items_written, bytes_received);
  
  return 0;
}

void PrintData(int startIndex, int endIndex){
  printf("------ data:\n");
  for( int i = startIndex; i <= endIndex ; i++){
    printf("%-6d | 0x%08X\n", i, data[i]);
  }
}

DataStatus WriteData(int bytes_received, std::string runName){

  const int words_received = bytes_received / 4;
  int index = 0;

  do{
    if( index >= words_received ) break;

    if(data[index] == 0xAAAAAAAA){ //==== DIG data

      int header[3];
      for( int i = 0; i < 3; i++) header[i] = ntohl(data[index+i+1]);

      int ch_id					          = (header[0] & 0x0000000F) >> 0;	// Word 1: 3..0
      int event_type				      = (header[2] & 0x03800000) >> 23;	// Word 3: 25..23

      if( ch_id >= 10 ) {
        std::string msg = "unknown";
        switch (ch_id){
          case 0xD : msg = "Run is done"; break;
          case 0xE : msg = "Empty"; break;
          case 0xF : {
            msg = "FIFO issue";
            if( event_type == 1) msg += " - overflow";
            if( event_type == 2) msg += " - underflow";
          }break;
        }
        printf("\033[34mDigitizer : Type %X data encountered (%s). skip.\033[0m\n", ch_id, msg.c_str());
        if( debug > 0 ) for( int i = 0 ; i < 4; i++) printf("%d | 0x%08X\n", index + i, ntohl(data[index+i]));
        index += 4; // Type F data is always 4 words.

        if( ch_id == 0xD ) return TypeD_RunIsDone;

        continue;
      }

      int board_id 			          = (header[0] & 0x0000FFF0) >> 4;	// Word 1: 15..4
      int packet_length_in_words	= (header[0] & 0x07FF0000) >> 16;	// Word 1: 26..16
      packet_length_in_words += 1; // include the header word

      #ifdef ENABLE_GEB_HEADER
        int timestamp_lower 		    = (header[1] & 0xFFFFFFFF) >> 0;	// Word 2: 31..0
        int timestamp_upper 		    = (header[2] & 0x0000FFFF) >> 0;	// Word 3: 15..0
        // int header_type				      = (header[2] & 0x000F0000) >> 16;	// Word 3: 19..16
        int packet_length_in_bytes	= packet_length_in_words * 4;

        gebData GEB_data;
        GEB_data.type = 0;
        GEB_data.length = packet_length_in_bytes;
        GEB_data.timestamp  = ((uint64_t)(timestamp_upper)) << 32;
        GEB_data.timestamp |=  (uint64_t)(timestamp_lower);
      #endif

      if (packet_length_in_words + index  > words_received){
        printf("\033[31m ERROR. DIG Data. Word received < packet length. \033[0m\n");
        PrintData(index, words_received-1);
        return DIG_inComplete;
      }
      
      int packet_length_in_bytes	= packet_length_in_words * 4; 
      
      int fileID = board_id * 100 + ch_id;
      if( outFileMap.find(fileID) == outFileMap.end() ){
        OutFile * newOutFile = new OutFile();
        newOutFile->runName = runName;
        outFileList.push_back(newOutFile);
        outFileMap[fileID] = outFileList.size() - 1;
        printf("Creating new OutFile for board %d, channel %d | fileID : %d, %u\n", board_id, ch_id, fileID, outFileMap[fileID]);
      }

      int fileOK = outFileList[outFileMap[fileID]]->OpenFile("", board_id, ch_id);
      if( fileOK < 0 ){
        printf("\033[1;31m !!!!! ERROR. Failed to open file for board %d, channel %d | fileID : %d \033[0m\n", board_id, ch_id, fileID);
        return DIG_fileOpenError;
      }
      #ifdef ENABLE_GEB_HEADER
      outFileList[outFileMap[fileID]]->Write(&GEB_data, sizeof(gebData));
      #endif
      outFileList[outFileMap[fileID]]->Write(&data[index], packet_length_in_bytes);
      
      index += packet_length_in_words; 

    }else if(data[index] == 0xAAAA0000){ //==== TRIG data

      int header[TRIG_DATA_SIZE];
      if (index + TRIG_DATA_SIZE > words_received) {
          printf("\033[31m ERROR. TRIG DATA. Not enough words for header. \033[0m\n");
          PrintData(index, words_received-1);
          return TRIG_inComplete;
      }

      for( int i = 0; i < TRIG_DATA_SIZE; i++) {
        header[i] = ntohl(data[index+i]);
        if( displayCount < max_displayCount ) printf("%2d | 0x%08X\n", index+i, header[i]);
      }

      int ch_id					    = 0x0;
      int board_id	        =  99;
      int header_type       = 0xE;
      
      int packet_length_in_words  = TRIG_PACKET_LENGTH; // 18 words
      
      int payload[TRIG_PACKET_LENGTH];

      payload[0] = 0xAAAAAAAA;
      
      payload[1]  = ch_id;
      payload[1] |= board_id << 4;
      payload[1] |= packet_length_in_words << 16;  // always 8 words payload
      
      payload[2]  = header[4]   ;
      payload[2] |= header[3]  << 16;  // timestamp 31:0
      
      payload[3]  = header[2]   ;  // timestamp 47:32
      payload[3] |= header_type  << 16; // header_type
      //payload[3] |= 0x0  << 23; // event_type
      payload[3] |= 3 << 26;
      
      payload[4] = (header[ 1] << 16) + header[ 5];  // trigType, wheel
      payload[5] = (header[ 6] << 16) + header[ 7];  // multiplicity, userRegister
      payload[6] = (header[ 8] << 16) + header[ 9];  // coarseTS, triggerBitMask
      
      payload[7] = (header[10] << 16) + header[11];  // tdcOffset[0], tdcOffset[1]
      payload[8] = (header[12] << 16) + header[13];  // tdcOffset[2], tdcOffset[3]
      payload[9] = (header[14] << 16) + header[15];  // vernierAB, vernierCD


      if( displayCount < max_displayCount ) { 
        printf("--------------------------------\n");
        for( int i = 0; i < TRIG_PACKET_LENGTH; i++) printf("%2d | 0x%08X\n", i, payload[i]);
      }

      displayCount ++;

      #ifdef ENABLE_GEB_HEADER
        gebData GEB_data;
        GEB_data.type = 0;
        GEB_data.length = packet_length_in_bytes;
        GEB_data.timestamp  = ((uint64_t)(header[2])) << 32;
        GEB_data.timestamp |= ((uint64_t)(header[3])) << 16;
        GEB_data.timestamp |=  (uint64_t)(header[4]);
      #endif

      if (TRIG_DATA_SIZE + index  > words_received){
        printf("\033[31m ERROR. TRIG DATA. Word received < packet length. \033[0m\n");
        PrintData(index, words_received-1);
        return TRIG_inComplete;
      }

      int fileID = board_id * 100 + ch_id;
      if( outFileMap.find(fileID) == outFileMap.end() ){
        OutFile * newOutFile = new OutFile();
        newOutFile->runName = runName;
        outFileList.push_back(newOutFile);
        outFileMap[fileID] = outFileList.size() -1;
        printf("Creating new OutFile for board %d, channel %d | fileID : %d, %u\n", board_id, ch_id, fileID, outFileMap[fileID]);
      }

      int fileOK = outFileList[outFileMap[fileID]]->OpenFile("_trig", board_id, ch_id);
      if( fileOK < 0 ){
        printf("\033[1;31m !!!!! ERROR. Failed to open file for board %d, channel %d | fileID : %d \033[0m\n", board_id, ch_id, fileID);
        return DIG_fileOpenError;
      }
      #ifdef ENABLE_GEB_HEADER
      outFileList[outFileMap[fileID]]->Write(&GEB_data, sizeof(gebData));
      #endif
      outFileList[outFileMap[fileID]]->Write(payload, sizeof(payload));      
      index += TRIG_DATA_SIZE;

    }else{

      printf("\033[31m ERROR. unknown data type. dump data. index : %d \033[0m\n", index);

      // do{
      //   printf("%-4d | 0x%08X\n", index, data[index]);
      //   index ++;
      // }while(index < words_received);

      DumpData(bytes_received);
      return UnknownDataType;
    }

    // printf("index : %d | %d\n", index, words_received);

  }while(index < words_received);

  return Good;
}

//###############################################################
int main(int argc, char **argv) {

  if( argc != 4){
    printf("usage:\n");
    printf("%s [IP] [Port] [file_prefix]\n\n", argv[0]);
    return -1;
  }

  std::string serverIP = argv[1];
  int serverPort = atoi(argv[2]);
  std::string runName = argv[3];

  outFileList.clear();

  printf("Connecting to %s:%d with run name %s\n", serverIP.c_str(), serverPort, runName.c_str());
  printf("Maximum file size is %lld bytes = %.2f GB\n", MAX_FILE_SIZE_BYTE, MAX_FILE_SIZE_BYTE/1024.0/1024.0/1024.0);
  printf("Default data size is %zu words = %zu Bytes = %.2f MB.\n", data.size(), data.size() * 4, data.size() * 4/1024.0/1024.0);

  #ifdef ENABLE_GEB_HEADER
  printf("GEB HEADER enabled.\n\n");
  #endif

  SetUpConnection(serverIP, serverPort);

  time_t startTime = time(NULL);
  time_t lastPrint = startTime;
  int displayTimeIntevral = 1; //sec

  DataStatus status = Good;
  
  int total_bytes_received = 0;
  do{
    //============ Send request and get data 
    int bytes_received = GetData();
    if( bytes_received > 0 ) total_bytes_received += bytes_received;

    // printf(" ========== Received %d Bytes = %d Words\n", bytes_received, bytes_received/4);

    //============ Write data to file
    if( bytes_received >= 0 ) status = WriteData(bytes_received, runName); // it decodes the data, and save the data for each channel.

    //============ Status
    time_t now = time(NULL);
    if (now - lastPrint >= displayTimeIntevral) { 
      time_t elapsed = now - startTime;
      char* timeStr = ctime(&now);
      if (timeStr) timeStr[strcspn(timeStr, "\n")] = '\0';  // Remove newline

      double totalFileSize = 0;
      for (size_t i = 0; i < outFileList.size(); i++) { totalFileSize += outFileList[i]->GetFileSize();}

      printf("======  %6.3f Mbytes | Received %d Bytes = %d Words | %24s | run Time: %ld sec\n", 
         totalFileSize/1024.0/1024.0, total_bytes_received, total_bytes_received/4, timeStr, elapsed);
      fflush(stdout);  // Make sure it prints immediately
      lastPrint = now;
      total_bytes_received = 0;
    }

    // usleep(100*1000);
  }while(status != TypeD_RunIsDone);
  // Close netSocket
  close(netSocket);

  printf("\033[31m==============End of Run. Closing files...\033[0m\n");
  
  // Close all open files
  double totalFileSize = 0;
  for( size_t i = 0; i < outFileList.size(); i++){  
    totalFileSize += outFileList[i]->GetFileSize();
    delete outFileList[i];
  }
  
  printf(" total files size : %6.3f Mbytes\n", totalFileSize/1024.0/1024.0);
  printf("==================== program ended.\n");
  
  return 0;
}
