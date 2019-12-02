# Image Processing Service

A simple image processing service implementation for AWS.

## Architecture

Image Processing is a common pattern with widely used reference architecture based on "serverless" pattern. In this particular case, AWS Cloud was chosen as a serverless infrastructure provider.

The suggested architecture provides a low-latency website response, decreases the cost of image optimization, manipulation, and processing. It uses AWS Lambda for dynamic image manipulation, CloudFront for global content delivery and Amazon S3 for reliable and durable cloud storage at a low cost.

<img src="docs/architecture.png"
     alt="Image Processing Service Architecture"
     style="max-width:600px" />

## <a name="implementation"></a>Implementation

Current implementation includes all architecture components except CloudFront.

Python is chosen as a language because of its performance within Lambdas, which was one of the key requirements. [Recent benchmarks](https://medium.com/the-theam-journey/benchmarking-aws-lambda-runtimes-in-2019-part-ii-50e796d3d11b) suggest that among all languages supported by Lambda service natively, Python is one of the fastest. It outperforms Node.js and Go in execution time and consistency.

[Chalice](https://github.com/aws/chalice) light-weight serverless framework is used to enable rapid development while maintaining the performance benefits of Python Lambdas.

Further up in the stack, [Pillow](https://github.com/python-pillow/Pillow) library is used for image processing and manipulation.

Finally, [Terraform](https://www.terraform.io) used for deployment of the complete solution with a single command. Terraform code can be easily extended to add CloudFront into the solution.

## APIs

Currently, the service API provides two key actions:

### 1. Add new image

`POST /api/v1/img`

**Request:**

&nbsp; &nbsp; `type` - (Required) Type of the image being added. Possible values: `base64` for Base64 encoded image, `url` for remote image, `uuid` for the image existing in the system. Currently, only `base64` is supported.

&nbsp; &nbsp; `data` - (Required) Value corresponding image `type`. E.g. for `base64` requests, the value should be Base64 encoded image.

```json
{
    "type": "base64",
    "data": "iVBORw0KGgoAAAANSUhEUgAA...."
}
```

**Response:**

Returns UUID of the newly added image.

```json
{
    "id": "5c51126a-9ee6-4d3d-acca-96f058253adb"
}
```

**Example:**

```
curl -X POST --header "Content-Type: application/json" \
     --data '{"type": "base64", "data": "iVBORw0KGgoAAAANSUhEUgAA...."}' \
     https://progimg.dev/api/v1/img
```

### 2. Retrieve existing image

Retrieve an image by UUID. A number of filters and transformations can be applied on the fly.

`GET /api/v1/img/{uuid}.{format}?{filter}={value}`

**Parameters:**

&nbsp; &nbsp; `uuid` - (Required) UUID of the existing image.

&nbsp; &nbsp; `format` - (Required) Format in which image should be returned, e.g. `jpg`, `png`, etc. Full list of supported formats available [here](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

&nbsp; &nbsp; `filter` - (Optional) Name and value of the filter which should be applied. Currently supported filters: `thumbnail`, `rotate`. Multiple filters can be specified in a single request.

**Example:**

```
curl 'https://progimg.dev/api/v1/img/5c51126a-9ee6-4d3d-acca-96f058253adb.png?thumbnail=200&rotate=180'
```

## Deploying

Requirements:

* Python 3.7.x
* Terraform 0.12
* AWS account with configured `awscli`

To deploy the complete solution to AWS, execute the following command:

```
make deploy
```

To destroy existing deployment and remove all resources from AWS:

```
make destroy
```

## Development

Initialise dev environment:

```
pip install -Ur src/requirements.txt -Ur src/requirements-dev.txt
```

Run service locally by emulating API Gateway and Lambda (supports hot reload):

```
make local
```

Run unit and integration tests:

```
make test
```

## <a name="faq"></a>FAQ

*Q: What language and frameworks are used to implement the service?*

A: Python and Chalice serverless framework. See motivation see [Implementation](#implementation) section above.

*Q: How uploaded images are stored?*

A: Original images are stored in S3. The original format of the image is preserved. The name replaced with UUID.

*Q: What can be improved in the code?*

A: CloudFront component can be added to cache manipulated images and serve them. This will massively improve performance. Further, Pillow can be replaced with [Pillow-SIMD](https://github.com/uploadcare/pillow-simd) which uses modern CPU instructions such as SSE4 and AVX2 to speed up image operations by the factor of 4-6.

*Q: What can build and test process be improved?*

A: Continuous Integration (CI) pipeline with end-to-end tests can improve the development process. CI can be triggered on commit as currently, the whole pipeline would take less than a minute to complete. Continuous Deployment pipeline can also be added to automatically deploy a healthy version using Terraform. Some of popular CI/CD tools are CircleCI are Jenkins.

*Q: How to deploy to a production environment?*

A: Add a new stage to [`src/.chalice/config.json`](src/.chalice/config.json) and configure it with production specific AWS policies. Versions tagged as release can be deployed to production automatically using Terraform and CI/CD tools of choice.

*Q: What tests are available in the project?*

A: A few basic [unit](src/test/unit) and [integration](src/test/integration) tests have been added. Integration tests must cover complete API functionality with positive and negative scenarios. Unit tests are used to test some internal functions in an isolated manner.
