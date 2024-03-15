<center><h1>lab1_report</h1></center>
<p align="right">21302010042</p>
<p align="right">侯斌洋</p>

<h3>（1）运行</h3>
<ol>
&emsp;
<li>IDEA中打开lab1文件夹，打开终端输入以下命令

```shell
orbd -ORBInitialPort 15000 -ORBInitialHost localhost
```
<br>
<li>lab1/.idea/runConfigurations 文件夹下存有项目运行配置，打开IDEA后右上角应有如下配置：<br>
<img src=image\run.png>
<br><br>
<li>Run server: 依次运行 NameNodeLauncher, DataNodeLauncher0, DataNodeLauncher1, DataNodeLauncher2启动服务器。DataNode数量可以修改，目前设置为3。<br>
<img src=image\run_server.png>
<br><br>
<li>Run tests: 在run server完成的基础上再执行以下测试，ClientTest，DataNodeTest，NameNodeTest分别为已提供的单元测试，NameNodeMetaFileTreeTest为对NameNode中用到的文件目录树的单元测试（虽然本次lab用不到文件目录&#x1F614;）<br>
<img src=image\run_test.png>
<br><br>
<li>Run shell: 在run server完成的基础上运行ClientShell，即可在ClientShell执行的窗口中开始交互式命令行操作。<br>
<img src=image\run_shell.png>
</ol>

<h3>（2）测试</h3>
<ol>
&emsp;
<li>ClientTest:无改动，可以正常通过测试。<br>
<img src=image\test_client.png>
<br><br>
<li>NameNodeTest: close接口修改以实现写时锁，由于api.idl中定义的string在实际运行过程中传递数据时不可为null,故有的检验null的地方改为了检验空字符串，如下：<br>

```java
assertEquals(fileInfo.file_path,"");
assertNotEquals(fileInfo2.file_path,"");
```
原本上面的代码是检验null与非null的。
实际测试的逻辑并没有修改，测试结果如下：
<img src=image\test_namenode.png>
<br><br>
<li>DataNodeTest: 修改了read的返回值，对原先的返回值进行了包装。因为在api.idl中已经定义了byteArray的大小，故返回的一定要为4096个字节，否则传输过程中会报错，然而如果直接用这4096个字节显然是不合理的，因为多余的完全为无效字节。我在这里包装了一下，使得再多返回一个指示有效字节的整数。

```java
struct ByteArrayWithLength{
    byteArray bytes;
    long byteNum;
};
```
实际测试的逻辑并没有修改，测试结果如下：
<img src=image\test_datanode.png>
<br><br>
<li>NameNodeMetaFileTreeTest: 对文件目录树的单元测试，结果如下：<br>
<img src=image\test_tree.png>
<br><br>
<li>Run shell，手动测试，结果如下：

```shell
C:\Users\21714\.jdks\corretto-1.8.0_392\bin\java.exe ...
Hello! Input command to operate
>>>open test.txt w
INFO: fd = 0
>>>read 0
INFO: read not allowed
INFO: read failed
>>>append 0 hello world
INFO: write done
>>>close 0
INFO: fd 0 closed
>>>open test.txt rw
INFO: fd = 0
>>>read 0
hello world
>>>exit
Bye~
```
之后的文件状态如下：
<img src=image\stats.png><br>
block0中的内容为hello world：
<img src=image\block0.png><br>
NodeMeta0.json中存放已使用的block信息，此时第0个block值应为true，其余的值为false:
<img src=image\nodemeta0.png><br>
fs_meta_file.json中存放文件目录树，此时只在root下有一个test.txt文件，如下：（增加了换行符以易于观察）
<img src=image\fs_tree.png><br>
</ol>

<h3>（3）实现思路</h3>
<ol>
<li>api定义如下：（注释中有详细介绍）

```java
module api {
    typedef octet byteArray[4*1024];
    struct FileMeta {           //文件在NameNode中存储的元数据
        string file_path;           //文件路径
        boolean is_new;             //是否为新建文件
        long writing_cookie;        //分配给用户的写识别号
        long file_size;             //文件大小，目前无用处，因为可以直接通过blockNum计算
        long block_num;             //文件使用的block数量
        long block_data_node[1000]; //文件使用的block所在的DataNode
        long block_id[1000];        //文件使用的block所在的DataNode的blockId
        string creat_time;          //创建时间
        string modify_time;         //修改时间
        string access_time;         //访问时间
    };
    struct ByteArrayWithLength{ //带长度的byteArray,解决返回值必须定长的问题
        byteArray bytes;            //返回的block，固定为4096个字节
        long byteNum;               //有效字节数
    };
    interface DataNode {
        //用户发起的读请求
        ByteArrayWithLength read(in long block_id);
        //用户发起的写请求
        boolean append(in long block_id, in ByteArrayWithLength byteArray, in string file_path);

        // From NameNode
        long check_free_size();         //NameNode发起的检查空余block数量的请求
        long alloc();                   //NameNode发起的分配block请求
        boolean free(in long block_id); //NameNode发起的释放block请求
    };
    interface NameNode {
        // From Client
        FileMeta open(in string file_path, in long mode);           //用户发起的打开文件请求
        boolean close(in string file_path, in long writing_cookie); //用户发起的关闭文件请求

        // 目录操作
        boolean mk_dir(in string dir_path);
        boolean del_dir(in string dir_path);
        boolean change_dir(in string old_dir_path,in string new_dir_path);
        boolean rename_dir(in string old_dir_path,in string new_dir_name);
        // 文件操作
        boolean mk_file(in string file_path);
        boolean del_file(in string file_path);
        boolean change_file(in string old_file_path,in string new_file_path);
        boolean rename_file(in string old_file_path,in string new_file_name);

        // from DataNode
        // 用户发出的写请求写的字节数超过了一个block，DataNode告知NameNode并交由NameNode处理。
        boolean file_increase(in string file_path, in ByteArrayWithLength byteArray,
            in long block_data_node, in long block_id, in boolean have_free);
    };
};
```
<li> fsImage设计：utils文件夹下有 NameNodeMetaFileNode.java 和 NameNodeMetaFileNode.java 文件，为文件目录树的实现，Node节点设计如下：

```java
public class NameNodeMetaFileNode {
    public FileMeta data;       //文件元数据
    public List<String> path;   //文件路径
    public boolean is_file;     //区分文件和目录
    public List<NameNodeMetaFileNode> children = null;  //子节点
}
```
Tree文件中则有一个根节点 root 和 NameNode元数据存放的文件地址，以及各种树操作：

```java
public class NameNodeMetaFileTree {
    public static NameNodeMetaFileNode root = null; //根节点
    private String meta_file_path = null;           //NameNode元数据文件地址

    //构造函数
    public NameNodeMetaFileTree(String meta_file_path){
        this.meta_file_path = meta_file_path;
    }

    //各种树操作...
    public void TreeOpt(){}
}
```
fsImage 即 NameNode元数据文件 NameNodeFile/fs_meta_file.json，为将 root 直接写入的 json文件，包含了一颗文件目录树，文件目录树下的每个节点存放对应文件的元数据，如上述Node节点的设计。
<br>
<li>文件及数据块的映射：每个文件以文件路径 path 字符串在文件目录树中标识，对应树中的一个节点，节点同时存放文件元数据。文件元数据中存放了该文件的 block 数量，每个 block 所在的 dataNode 以及在该 dataNode 中对应的blockId。如下：

```java
struct FileMeta {           //文件在NameNode中存储的元数据
    string file_path;           //文件路径
    boolean is_new;             //是否为新建文件
    long writing_cookie;        //分配给用户的写识别号
    long file_size;             //文件大小，目前无用处，因为可以直接通过blockNum计算
    long block_num;             //文件使用的block数量
    long block_data_node[1000]; //文件使用的block所在的DataNode
    long block_id[1000];        //文件使用的block所在的DataNode的blockId
    string creat_time;          //创建时间
    string modify_time;         //修改时间
    string access_time;         //访问时间
};
```
例如，若某个文件有 1 个block，则 blockNum 为1；blockDataNode[0] 中存放了该 block 所在的 dataNode， blockId[0] 则存放了该 block 所在的 dataNode 中具体的 blockId 索引。从而就将文件和 block 之间建立起了映射。<br><br>
<li>NameNode的设计: NameNode中包含一个 NameNodeMetaFileTree 结构，用于在内存中存储文件目录树。在分配新的 block 时 NameNode 检测所有的 dataNode 并选出空余 block 最多的 dataNode，调用对应 dataNode 的 alloc() 方法进行分配。因此为一种负载均衡的分配策略。

```java
//寻找空闲最多的dataNode，分配空间
private int [] alloc(){
    GetDataNode();
    int [] new_block = new int[]{0,0};
    int max_free_node=0;
    int max_free_size=0;
    for(int i=0;i<MAX_DATA_NODE;i++){
        int free_size = dataNodes[i].check_free_size();
        if(free_size>max_free_size){
            max_free_size=free_size;
            max_free_node=i;
        }
    }
    new_block[0] = max_free_node;
    new_block[1] = dataNodes[max_free_node].alloc();
    return new_block;
}
```
<br>
<li>DataNode设计：DataNode中包含其自身对应的 dataNodeId 和 用于在内存中存储当前已分配的 block 信息的 boolean [] block_used结构。

```java
private int dateNodeId;
private boolean [] block_used = new boolean[MAX_BLOCK_NUM];
```
block_used 对应 dataNode 的元数据文件 NodeMeta.json，记录当前已分配的 block。每个 block 为一个文件，如第0个 block 为文件 block0，block 文件与NodeMeta.json文件位于同一文件夹下。在append函数中限制了每个文件可以写的最大字节数为 4096。分配新 block 时只需从头开始遍历 block_used 数组，找到一个 false 即可，然后根据对应 blockId 创建新文件。读写数据时只需根据 blockId 对对应的文件进行操作即可。
<br>
<li>Client设计：Client中包含3个数组用于记录目前打开的文件数据，cur_open_file_meta 记录文件元数据，cur_fd_used 记录文件占用的 fd号， cur_fd_privilege记录打开文件时指定的权限。

```java
private static FileMeta[] cur_open_file_meta = new FileMeta[MAXFDNUM];
private static boolean[] cur_fd_used = new boolean[MAXFDNUM];
private static int [] cur_fd_privilege = new int[MAXFDNUM];
```
&emsp;&emsp;打开文件时，若该文件已打开，则返回之前的 fd 。若打开失败则返回 -1。若为第一次打开且打开成功，则在上述三个数据结构中记录已打开的文件数据。
&emsp;&emsp;读取文件时，首先检查权限，再根据保存的文件元数据向 dataNode 发送请求，依照上述的文件与 block 的映射关系，遍历 blockNum 数量的 block，依次向对应的 dataNode 发送请求并将接收到的所有 byteArray拼接到一起然后返回给用户。
&emsp;&emsp;写文件时，与读文件类似，首先检查权限，再根据保存的文件元数据向最末尾的 block 对应的 dataNode发送写请求，因为最末尾的 block 就对应着文件的末尾。
&emsp;&emsp;关闭文件时，只需向NameNode发送请求并清除本地保存的已打开文件的数据即可。
</ol>
<h3>（4）具体实现详见代码</h3>
&emsp;已完成所有要求的接口，且已通过单元测试。<br>
&emsp;NameNode中对目录的各种操作也已完成，但额外的目录操作暂未进行单元测试。
<br><br>
<h3>（5）关于第二次提交所做的改动</h3>
&emsp;在ClientTest中增加了对于写多个块的内容的测试，并在测试的过程中修正了一些代码以维持正确性。以下测试主要是为了检验在同一个DataNode中读写2个块和在不同的DataNode中读写2个块时程序是否能正常运行，作为ClientTest的补充测试。

```java
//测试读写两个block的大小
//分别设置DataNodeImpl.java中的MAX_BLOCK_NUM为1和100
//为1时分别在node0和node1中生成了两个block
//为100时在node0中生成了两个block
//两种情况下测试均能通过。
@Test
public void testWriteTwoBlock(){
    String filename = FileSystem.newFilename();
    int fd = client.open(filename,0b11);
    
    //第一个block
    byte[] block0 = new byte[4096];
    block0[0]='h';
    block0[4095]='h';
    //第二个block
    byte[] block1 = new byte[4096];
    block1[0]='w';
    block1[4095]='w';
    
    //写两个block
    client.append(fd,block0);
    client.append(fd,block1);
    
    //读取所有数据
    byte[] read = client.read(fd);
    
    //检验运行结果
    assertNotNull(read);
    assertEquals(4096*2, read.length);
    assertEquals('h', read[0]);
    assertEquals('h', read[4095]);
    assertEquals('w', read[4096]);
    assertEquals('w', read[4096*2-1]);
    client.close(fd);
}
```
