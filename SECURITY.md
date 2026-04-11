# Security Guidelines

## Rotating Exposed Credentials
1. **Immediate Action**: If you suspect that your credentials have been exposed, immediately revoke them.
2. **Generate New Credentials**: Create new credentials from the service provider's console.
3. **Update Application**: Update your application configuration to use the new credentials.
4. **Inform Team**: Notify team members about the change to ensure that everyone is using the updated credentials.
5. **Periodic Review**: Regularly review and rotate secrets, even if they have not been compromised, to minimize potential risks.

## Setting Up .env File with python-dotenv
To manage your application's environment variables securely, follow these steps:
1. **Install python-dotenv**: If you haven't yet, install the package using pip:
   ```bash
   pip install python-dotenv
   ```
2. **Create a `.env` file** at the root of your project:
   ```bash
   touch .env
   ```
3. **Add your environment variables** to the `.env` file:
   ```plaintext
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ```
4. **Load environment variables in your application**:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()
   database_url = os.getenv('DATABASE_URL')
   ```
5. **Never commit your `.env` file** to version control. Add it to your `.gitignore`:
   ```plaintext
   # .gitignore
   .env
   ```

## Best Practices for Production Deployment
1. **Use Environment Variables**: Store sensitive configuration data like API keys and database passwords in environment variables.
2. **Enable HTTPS**: Ensure that your application uses HTTPS to encrypt data in transit.
3. **Regular Updates**: Keep your dependencies and server updated to protect against known vulnerabilities.
4. **Limit Access**: Implement the principle of least privilege by restricting access to sensitive resources.
5. **Monitor and Log**: Set up monitoring and logging to detect and respond to security incidents swiftly.
6. **Regular Security Audits**: Conduct periodic security audits to find and fix potential vulnerabilities in the code.
7. **Backup Data**: Regularly back up your application and database to prevent data loss in case of an attack or failure.